# FileMgr CLI Prototype (Windows focused)

간단한 대화형 CLI 파일 관리 프로그램 프로토타입입니다. 안전한 삭제(휴지통 이동), 강제 삭제(권한 취득 + 삭제), 잠금 확인(handle.exe 연동), 미리보기 및 용량 확인 등의 기능을 제공합니다.

⚠️ 이 도구는 강력한 파일 삭제 기능을 포함합니다. 중요한 데이터가 있을 경우 미리 백업하세요.

## 설치/준비
- Python 3.8 이상을 권장합니다.
- Windows에서 `takeown`과 `icacls` 명령을 사용하려면 관리자 권한으로 실행하세요.
- 파일 잠금 해제 기능을 사용하려면 [Sysinternals Handle](https://learn.microsoft.com/sysinternals/downloads/handle) (handle.exe)을 PATH에 추가하세요.

## 실행
Interactive shell
```powershell
python filemgr.py --interactive
# 또는
python filemgr.py -i
```

간단한 명령 예:
- `ls M:\temp\Takeout` - 목록 보기
- `preview M:\temp\Takeout` - 상위 20개 항목 미리보기
- `size M:\temp\Takeout` - 폴더 크기 확인
- `rm M:\temp\Takeout` - 휴지통(.filemgr_trash)으로 이동 (복원 가능)
- `rm! M:\temp\Takeout` - 강제 삭제(ownership을 취득하고 삭제 시도)
- `takeown M:\temp\Takeout` - Windows에서 소유권을 취득하고 권한 부여 시도
- `handles M:\temp\Takeout` - handle.exe 출력창을 보여줌 (설치 필요)

1. 기본 동작은 휴지통(드라이브 루트의 `.filemgr_trash`)으로 이동합니다. 이는 완전 삭제를 방지하고 복구 가능하도록 합니다.
2. 강제 삭제 옵션은 `takeown` + `icacls`를 활용하여 파일 소유권을 변경하고 재시도합니다.
3. 잠금 문제를 해결하려면 `handles` 명령으로 잠금을 유발하는 프로세스를 찾고 종료하세요.

## 지원/확장 아이디어
- GUI를 제공하거나 `prompt_toolkit` 기반의 색상/탭 완성 추가
- 전체 삭제 로그와 복원 명령 추가
- 예약 삭제, 필터(파일 확장자 제외/포함), 안전 규칙(특정 경로 예외) 추가
- 운영 체제에 따라 MoveFileEx로 재부팅 시 삭제 예약


## 기여
이 스크립트는 학습/프로토타입 목적입니다. 사용 전 소스 검토를 권장합니다.

## Git 로컬 시작 가이드
프로젝트를 로컬에서 시작하고 GitHub에 올리기 위한 기본 단계:

1. 로컬 저장소 초기화 및 첫 커밋
```powershell
cd path\to\filemgr-prototype
git init -b main
git add .
git commit -m "Initial commit: FileMgr prototype"
git branch develop
git checkout develop
```

2. 풀 리퀘스트(Feature 브랜치 예제)
```powershell
git checkout -b feature/cli
# 변경 작업 후
git add .; git commit -m "Add feature X"
git push -u origin feature/cli
```

3. 원격 저장소에 push 및 PR 생성
```powershell
git remote add origin git@github.com:youruser/filemgr.git
git push -u origin main
git push -u origin develop
```

4. PR 템플릿과 CI가 준비되었습니다. 원격 저장소에 push하면 GitHub Actions가 테스트를 자동으로 실행합니다.

---

안내: 저는 프로젝트 로컬 초기화 및 브랜치/CI/템플릿 설정까지 완료했습니다. 원하시면 `git remote add` 후에 GitHub에 push할 명령어도 만들어 드립니다.