# 📱 핸드폰에서 쓰도록 배포하기 (Streamlit Cloud + Supabase)

이 가이드대로 따라 하면, 인터넷 어디서나 핸드폰으로 접속해 기록할 수 있고,
데이터는 영구 보관됩니다. **모두 무료**입니다. 약 20~30분 소요.

순서: ① Supabase에서 DB 만들기 → ② GitHub에 코드 올리기 → ③ Streamlit Cloud에 배포

---

## ① Supabase 에서 데이터베이스 만들기 (데이터 영구 보관소)

1. https://supabase.com 접속 → **Start your project** → GitHub 또는 이메일로 가입
2. **New project** 클릭
   - Name: 아무거나 (예: `record-app`)
   - **Database Password**: 비밀번호를 정하고 **꼭 따로 메모**해 두세요 (나중에 필요)
   - Region: `Northeast Asia (Seoul)` 추천
   - **Create new project** (1~2분 기다리면 생성됨)
3. 왼쪽 메뉴 맨 아래 **⚙️ Project Settings** → **Database** 클릭
4. **Connection string** 항목에서 **URI** 탭 선택 → 주소를 복사
   - 형태: `postgresql://postgres.xxxx:[YOUR-PASSWORD]@aws-0-...pooler.supabase.com:6543/postgres`
   - 주소 안의 `[YOUR-PASSWORD]` 부분을 **2번에서 메모한 실제 비밀번호로 바꿔** 두세요.
   - 💡 `Transaction` 모드(포트 6543)를 권장합니다.

이 완성된 주소를 잠시 메모장에 보관하세요. ③에서 씁니다.

---

## ② GitHub 에 코드 올리기

> 코드는 이미 이 폴더에서 git 커밋까지 끝나 있습니다. 원격 저장소에 올리기만 하면 됩니다.

1. https://github.com 접속 → 가입/로그인
2. 오른쪽 위 **+** → **New repository**
   - Repository name: `record-app` (아무거나)
   - **Private** 선택 (개인 데이터 앱이므로 비공개 권장)
   - 나머지는 비워두고 **Create repository**
3. 생성 후 나오는 화면에서 `…or push an existing repository` 부분의 주소를 확인하고,
   **이 프로젝트 폴더의 터미널**에서 아래를 실행하세요 (`<당신-주소>` 부분만 교체):

   ```bash
   git remote add origin https://github.com/<당신-아이디>/record-app.git
   git branch -M main
   git push -u origin main
   ```
   - push 할 때 GitHub 로그인(또는 토큰)을 물어볼 수 있습니다.
   - ✅ `secrets.toml` 과 `record.db` 는 자동으로 제외되어 올라가지 않습니다(비밀 안전).

---

## ③ Streamlit Community Cloud 에 배포

1. https://share.streamlit.io 접속 → **Continue with GitHub** 로 로그인
2. **Create app** → **Deploy a public app from GitHub** 선택
3. 설정:
   - **Repository**: 방금 만든 `record-app` 선택
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. 배포 전에 **Advanced settings**(또는 배포 후 앱 메뉴 → **Settings → Secrets**) 클릭 →
   아래 내용을 붙여넣으세요. **두 값을 본인 것으로 교체**:

   ```toml
   app_password = "원하는_로그인_비밀번호"

   [database]
   url = "postgresql://postgres.xxxx:실제비번@aws-0-...pooler.supabase.com:6543/postgres"
   ```
   - `app_password`: 앱에 로그인할 때 칠 비밀번호 (직접 정함)
   - `[database] url`: ①에서 완성해 둔 Supabase 주소
5. **Deploy** 클릭 → 1~3분 기다리면 `https://<이름>.streamlit.app` 주소가 생깁니다.

---

## 🎉 완료 후

- 핸드폰 브라우저에서 그 `.streamlit.app` 주소로 접속 → 비밀번호 입력 → 기록 시작!
- **홈 화면에 추가**하면 앱 아이콘처럼 쓸 수 있어요:
  - 아이폰(Safari): 공유 버튼 → "홈 화면에 추가"
  - 안드로이드(Chrome): 메뉴(⋮) → "홈 화면에 추가"

## 참고

- 며칠간 아무도 접속 안 하면 앱이 잠자기에 들어갑니다. 다시 접속하면 수십 초 뒤 깨어납니다.
- 코드를 고쳐 GitHub에 push 하면 Streamlit Cloud가 **자동으로 재배포**합니다.
  (데이터는 Supabase에 있으므로 재배포해도 안 날아갑니다.)
- 로컬에서 테스트할 때는 `.streamlit/secrets.toml` 의 `app_password`(기본값 `test1234`)로 로그인하고,
  데이터는 로컬 `record.db` 에 저장됩니다(클라우드와 분리됨).
