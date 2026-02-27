TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_guide",
            "description": "식스샵 프로 플랫폼에 관한 도움말을 검색한다. 기능 사용법, 용어 설명, 운영 방법 등 플랫폼과 관련된 모든 질문에 활용한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색할 질문 또는 키워드",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_product",
            "description": "새로운 상품을 등록한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "상품명",
                    },
                    "price": {
                        "type": "integer",
                        "description": "상품 가격 (원)",
                    },
                },
                "required": ["name", "price"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_products",
            "description": "등록된 상품 목록을 조회한다. 특정 상품을 찾을 때는 name으로 검색한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["active", "inactive"],
                        "description": "상품 상태 필터. 사용자가 명시적으로 상태를 언급한 경우에만 지정한다. 미지정 시 전체 상태 조회.",
                    },
                    "name": {
                        "type": "string",
                        "description": "상품명 검색 키워드 (부분 일치). 가격·상태 등 상품명이 아닌 조건은 넣지 않는다.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_product",
            "description": "기존 상품의 정보를 수정한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "상품 ID (예: PRD-1)",
                    },
                    "name": {
                        "type": "string",
                        "description": "변경할 상품명",
                    },
                    "price": {
                        "type": "integer",
                        "description": "변경할 가격 (원)",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "inactive"],
                        "description": "변경할 상태",
                    },
                },
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_product",
            "description": "상품을 삭제한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "삭제할 상품 ID (예: PRD-1)",
                    },
                },
                "required": ["id"],
            },
        },
    },
]
