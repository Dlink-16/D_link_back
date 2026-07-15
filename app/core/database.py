"""SQLite 엔진과 SQLAlchemy 세션의 생성 주기를 관리한다."""

import os
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session

from app.core.config import get_settings

# 운영 DB와 테스트용 임시 DB가 서로 엔진을 공유하지 않도록 경로별로 보관한다.
_engines: dict[Path, Engine] = {}


def get_database_path(db_path: Optional[os.PathLike | str] = None) -> Path:
    """명시된 경로 또는 환경변수에 설정된 DB 경로를 반환한다."""
    if db_path is not None:
        return Path(db_path)

    return get_settings().tourapi_db_path


def get_engine(db_path: Optional[os.PathLike | str] = None) -> Engine:
    """DB 경로별 SQLite 엔진을 생성하거나 기존 엔진을 재사용한다."""
    path = get_database_path(db_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    engine = _engines.get(path)
    if engine is None:
        engine = create_engine(
            f"sqlite:///{path.as_posix()}",
            # FastAPI 요청은 서로 다른 스레드에서 같은 연결을 사용할 수 있다.
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(engine, "connect")
        def enable_foreign_keys(dbapi_connection, _connection_record) -> None:
            """SQLite 연결마다 선언된 외래키 제약을 활성화한다."""
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.close()

        _engines[path] = engine

    return engine


def get_session(db_path: Optional[os.PathLike | str] = None) -> Session:
    """지정한 DB 엔진에 연결된 SQLAlchemy 세션을 생성한다."""
    return Session(get_engine(db_path))


def get_db_session() -> Generator[Session, None, None]:
    """요청 종료 시 자동으로 닫히는 FastAPI 세션 의존성을 제공한다."""
    with get_session() as session:
        yield session


def init_db(db_path: Optional[os.PathLike | str] = None) -> Path:
    """등록된 ORM 모델을 기준으로 존재하지 않는 테이블을 생성한다."""
    # 모델 패키지를 여기서 불러와 순환 참조 없이 모든 테이블을 등록한다.
    from app.models import Base

    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return get_database_path(db_path)
