"""데이터 입출력 모듈 (SQLAlchemy 기반).

로컬에서는 SQLite 파일(record.db)을, 클라우드 배포 시에는 Postgres(Supabase)를
같은 코드로 사용한다. 어느 DB를 쓸지는 연결 주소(DATABASE_URL)로 결정된다.

연결 주소 우선순위:
  1. Streamlit secrets 의 [database] url   (클라우드 배포 환경)
  2. 환경변수 DATABASE_URL
  3. 둘 다 없으면 로컬 SQLite (record.db)
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import (
    Column,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    delete,
    insert,
    inspect,
    select,
    text,
)
from sqlalchemy.engine import Engine

# ---------- 테이블 정의 (SQLite/Postgres 공통) ----------
metadata = MetaData()

exercise = Table(
    "exercise", metadata,
    Column("id", Integer, primary_key=True),       # 자동 증가 (양쪽 DB 자동 처리)
    Column("date", String, nullable=False),        # YYYY-MM-DD
    Column("name", String, nullable=False),        # 운동 종목 (풀업, 벤치프레스, 본운동 ...)
    Column("weight", Float),                        # 중량(kg) — 중량 기반 종목만
    Column("detail", String),                       # 부가정보 — 본운동의 부위(가슴/등/어깨/하체)
    Column("minutes", Integer),                    # (구버전 호환, 미사용)
    Column("sets", Integer),                         # (구버전 호환, 미사용)
    Column("memo", String),                          # (구버전 호환, 미사용)
)

diet = Table(
    "diet", metadata,
    Column("id", Integer, primary_key=True),
    Column("date", String, nullable=False),
    Column("meal", String, nullable=False),        # 끼니
    Column("food", String, nullable=False),        # 음식 내용
    Column("calories", Integer),                    # 칼로리(kcal)
    Column("memo", String),
)

weight = Table(
    "weight", metadata,
    Column("id", Integer, primary_key=True),
    Column("date", String, nullable=False),
    Column("weight_kg", Float, nullable=False),     # 몸무게(kg)
    Column("memo", String),
)

_TABLES = {"exercise": exercise, "diet": diet, "weight": weight}

# 엔진은 한 번만 생성해 재사용한다.
_engine: Engine | None = None


def _database_url() -> str:
    """사용할 DB 연결 주소를 결정한다."""
    # 1) Streamlit secrets (배포 환경)
    try:
        import streamlit as st

        if "database" in st.secrets and "url" in st.secrets["database"]:
            return str(st.secrets["database"]["url"])
    except Exception:
        pass
    # 2) 환경변수
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    # 3) 로컬 기본값: SQLite
    return f"sqlite:///{Path(__file__).parent / 'record.db'}"


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        url = _database_url()
        # Supabase 등에서 'postgres://' 형식을 줄 때 SQLAlchemy 표준으로 보정한다.
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def init_db() -> None:
    """테이블이 없으면 생성하고, 구버전 스키마에 누락된 칼럼을 보충한다."""
    metadata.create_all(get_engine())
    _migrate()


def _migrate() -> None:
    """이미 만들어진 exercise 테이블에 weight/detail 칼럼이 없으면 추가한다.

    create_all 은 '없는 테이블'만 만들 뿐 '없는 칼럼'은 추가하지 않으므로,
    구버전 스키마로 배포된 DB(예: Supabase)를 위해 별도로 보정한다.
    """
    eng = get_engine()
    existing = {c["name"] for c in inspect(eng).get_columns("exercise")}
    add = []
    if "weight" not in existing:
        add.append("ALTER TABLE exercise ADD COLUMN weight FLOAT")
    if "detail" not in existing:
        add.append("ALTER TABLE exercise ADD COLUMN detail TEXT")
    if add:
        with eng.begin() as conn:
            for stmt in add:
                conn.execute(text(stmt))


# ---------- 입력 ----------
def add_exercise(date, name, weight=None, detail=None) -> None:
    """운동 한 종목을 기록한다. weight 는 중량 기반 종목, detail 은 본운동 부위."""
    with get_engine().begin() as conn:
        conn.execute(insert(exercise).values(
            date=date, name=name, weight=weight, detail=detail))


def get_last_weight(name) -> float | None:
    """해당 종목을 가장 최근에 기록했을 때의 중량을 반환한다(없으면 None)."""
    stmt = (
        select(exercise.c.weight)
        .where(exercise.c.name == name, exercise.c.weight.isnot(None))
        .order_by(exercise.c.date.desc(), exercise.c.id.desc())
        .limit(1)
    )
    with get_engine().connect() as conn:
        row = conn.execute(stmt).first()
    return float(row[0]) if row and row[0] is not None else None


def add_diet(date, meal, food, calories, memo) -> None:
    with get_engine().begin() as conn:
        conn.execute(insert(diet).values(
            date=date, meal=meal, food=food, calories=calories, memo=memo))


def add_weight(date, weight_kg, memo) -> None:
    with get_engine().begin() as conn:
        conn.execute(insert(weight).values(
            date=date, weight_kg=weight_kg, memo=memo))


# ---------- 조회 / 삭제 ----------
def get_df(table: str) -> pd.DataFrame:
    """테이블 전체를 날짜 내림차순 DataFrame 으로 반환한다."""
    t = _TABLES.get(table)
    if t is None:
        raise ValueError(f"알 수 없는 테이블: {table}")
    stmt = select(t).order_by(t.c.date.desc(), t.c.id.desc())
    with get_engine().connect() as conn:
        return pd.read_sql(stmt, conn)


def delete_row(table: str, row_id: int) -> None:
    """특정 기록 한 건을 삭제한다."""
    t = _TABLES.get(table)
    if t is None:
        raise ValueError(f"알 수 없는 테이블: {table}")
    with get_engine().begin() as conn:
        conn.execute(delete(t).where(t.c.id == row_id))
