from fastapi.openapi.utils import get_openapi


def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="동영상 플랫폼 API",
        version="1.0.0",
        description="""
            기업 고객을 위한 영상 관리 플랫폼의 API입니다.  
            어드민과 일반 유저를 구분하여 역할에 맞는 기능을 제공합니다.
            
            ### Auth
            - JWT 기반 로그인 API를 제공합니다.
            
            ### User
            - **어드민**: 유저 생성, 수정, 삭제를 수행할 수 있습니다.
            - **일반 유저**: 본인의 계정을 수정하거나 삭제할 수 있습니다.
            
            ### Organization
            - 새로운 조직(기업) 등록이 가능합니다.
            - 유료 플랜 구독을 통해 프리미엄 기능(삭제 영상 복구 등)을 활성화할 수 있습니다.
            
            ### Video
            - **어드민**: 영상 등록, 수정, 삭제가 가능합니다.
            - **일반 유저**: 영상 조회가 가능하며, 조회 시 포인트가 지급됩니다.
        """,
        routes=app.routes,
    )

    # JWT 인증 헤더 추가
    openapi_schema["components"]["securitySchemes"]["OAuth2PasswordBearer"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"OAuth2PasswordBearer": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema
