---
name: api-design-principles
description: "Defines resource naming conventions, designs REST endpoints and GraphQL schemas, structures error responses with proper HTTP status codes, plans pagination and filtering strategies, and establishes API versioning and contracts. Use when designing new APIs, reviewing OpenAPI/Swagger specs, structuring routes and endpoints, defining API contracts, or establishing versioning and error code standards."
---

# API Design Principles

## Workflow

Follow these steps sequentially when designing or reviewing an API:

### Step 1: Define Resources and Naming

Identify domain entities as plural nouns. Map them to a URL hierarchy:

```
GET    /api/users              # List collection (paginated)
POST   /api/users              # Create resource
GET    /api/users/{id}         # Get single resource
PUT    /api/users/{id}         # Replace resource
PATCH  /api/users/{id}         # Partial update
DELETE /api/users/{id}         # Remove resource
GET    /api/users/{id}/orders  # Nested sub-collection
```

### Step 2: Design Pagination and Filtering

Every collection endpoint must support pagination. Use cursor-based pagination for large or real-time datasets, offset-based for simpler cases:

```python
# Offset-based pagination response structure
{
    "items": [...],
    "total": 142,
    "page": 2,
    "page_size": 20,
    "pages": 8
}

# Cursor-based pagination response structure (Relay-style)
{
    "edges": [{"node": {...}, "cursor": "abc123"}],
    "pageInfo": {
        "hasNextPage": true,
        "endCursor": "abc123"
    },
    "totalCount": 142
}
```

Support filtering via query parameters: `?status=active&created_after=2024-01-01&search=term&sort=name:asc`.

### Step 3: Structure Error Responses

Return a consistent error envelope across all endpoints:

```json
{
    "error": "ValidationError",
    "message": "Request validation failed",
    "details": {
        "errors": [
            {"field": "email", "message": "Invalid email format"}
        ]
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/users"
}
```

Map errors to correct HTTP status codes: 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 409 (conflict), 422 (validation), 429 (rate limited), 500 (internal).

### Step 4: Plan Versioning Strategy

Choose one strategy and apply it consistently:

- **URL path** (most common): `/api/v1/users` - simple, explicit, easy to route
- **Header**: `Accept: application/vnd.api+json; version=1` - cleaner URLs, harder to test
- **Query param**: `/api/users?version=1` - easy to test, clutters query string

Document deprecation timelines in API contracts. Use `Sunset` and `Deprecation` headers to signal upcoming removals.

### Step 5: Design GraphQL Schema (if applicable)

Define types, connections, inputs, and payloads:

```graphql
type User {
  id: ID!
  email: String!
  name: String!
  orders(first: Int = 20, after: String): OrderConnection!
}

type OrderConnection {
  edges: [OrderEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}

input CreateUserInput {
  email: String!
  name: String!
}

type CreateUserPayload {
  user: User
  errors: [Error!]
}
```

Use DataLoaders to prevent N+1 queries on relationship fields. Return structured errors in mutation payloads rather than throwing exceptions.

### Step 6: Validate with Checklist

Before finalizing, verify:

- [ ] All collection endpoints are paginated
- [ ] Error responses use a consistent envelope format
- [ ] Resource names are plural nouns, no verbs in URLs
- [ ] Versioning strategy is documented and applied
- [ ] Rate limiting headers are included (`X-RateLimit-Limit`, `X-RateLimit-Remaining`)
- [ ] OpenAPI/Swagger spec is generated and accurate
- [ ] Authentication and authorization are defined per endpoint
- [ ] CORS policy is configured for browser clients
- [ ] Idempotency keys are supported for mutation endpoints (POST/PUT)

## Resources

- **references/rest-best-practices.md**: Comprehensive REST API design guide
- **references/graphql-schema-design.md**: GraphQL schema patterns and anti-patterns
- **references/api-versioning-strategies.md**: Versioning approaches and migration paths
- **assets/rest-api-template.py**: FastAPI REST API template
- **assets/graphql-schema-template.graphql**: Complete GraphQL schema example
- **assets/api-design-checklist.md**: Pre-implementation review checklist
- **scripts/openapi-generator.py**: Generate OpenAPI specs from code
