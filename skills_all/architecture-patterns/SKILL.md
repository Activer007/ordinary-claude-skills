---
name: architecture-patterns
description: "Apply Clean Architecture, Hexagonal (ports and adapters), onion architecture, layered architecture, and DDD patterns to backend systems. Define bounded contexts, create port/adapter interfaces, organize dependency layers, separate domain from infrastructure, enforce dependency inversion, and structure project layout for separation of concerns. Use when designing new services, refactoring tightly coupled code, planning microservices decomposition, or establishing project structure conventions."
---

# Architecture Patterns

## Workflow

Follow these steps sequentially when applying architecture patterns to a codebase:

### 1. Identify domain boundaries and define bounded contexts

- Map the business domain into distinct bounded contexts with clear responsibilities
- Define the ubiquitous language for each context
- Determine context relationships (shared kernel, customer-supplier, anti-corruption layer)

### 2. Define core entities and value objects

- Model entities (objects with identity and lifecycle) in the domain layer
- Extract value objects (immutable, identity-less) for concepts like Money, Email, Address
- Keep all business rules inside entities and value objects -- no logic in services or controllers

### 3. Create repository interfaces (ports)

- Define abstract interfaces in the domain layer for all external dependencies
- Ports include: data persistence, external APIs, messaging, notifications
- Domain code depends only on these interfaces, never on concrete implementations

### 4. Implement adapters

- Write concrete implementations of each port (Postgres repository, Stripe gateway, SQS publisher)
- Adapters live in an outer layer and import the domain -- never the reverse
- Create test doubles (in-memory repositories, mock gateways) implementing the same ports

### 5. Wire use cases to orchestrate business logic

- Each use case class receives ports via constructor injection
- Use cases coordinate domain objects and ports to fulfill a single application operation
- Return result objects, not raw domain entities, to decouple callers from domain internals

### 6. Validate architecture constraints

- **Dependency rule**: all dependencies point inward (infrastructure -> application -> domain)
- **Domain purity**: domain layer has zero framework imports
- **Interface segregation**: ports are small and focused on one capability
- **Thin controllers**: HTTP/CLI handlers only translate input/output and delegate to use cases

## Reference Implementation

This trimmed example shows the key relationships: entity -> port -> use case -> adapter.

```python
# domain/entities/user.py — Core entity, no framework dependencies
@dataclass
class User:
    id: str
    email: str
    name: str
    is_active: bool = True

    def deactivate(self):
        self.is_active = False

# domain/interfaces/user_repository.py — Port (abstract interface in domain)
class IUserRepository(ABC):
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]: ...
    @abstractmethod
    async def save(self, user: User) -> User: ...

# use_cases/create_user.py — Orchestrates domain + ports
class CreateUserUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def execute(self, email: str, name: str) -> User:
        if await self.user_repo.find_by_email(email):
            raise ValueError("Email already exists")
        user = User(id=str(uuid4()), email=email, name=name)
        return await self.user_repo.save(user)

# adapters/postgres_user_repository.py — Adapter (implements port)
class PostgresUserRepository(IUserRepository):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def find_by_email(self, email: str) -> Optional[User]:
        row = await self.pool.fetchrow("SELECT * FROM users WHERE email=$1", email)
        return User(**row) if row else None

    async def save(self, user: User) -> User:
        await self.pool.execute(
            "INSERT INTO users (id,email,name,is_active) VALUES ($1,$2,$3,$4) "
            "ON CONFLICT (id) DO UPDATE SET email=$2, name=$3, is_active=$4",
            user.id, user.email, user.name, user.is_active)
        return user
```

## Directory Structure

```
app/
├── domain/           # Entities, value objects, ports (interfaces)
│   ├── entities/
│   ├── value_objects/
│   └── interfaces/
├── use_cases/        # Application business rules
├── adapters/         # Port implementations (DB, APIs, messaging)
│   ├── repositories/
│   ├── controllers/
│   └── gateways/
└── infrastructure/   # Framework config, logging, DI wiring
```

## Resources

- **references/clean-architecture-guide.md**: Detailed layer breakdown
- **references/hexagonal-architecture-guide.md**: Ports and adapters patterns
- **references/ddd-tactical-patterns.md**: Entities, value objects, aggregates
- **assets/clean-architecture-template/**: Complete project structure
- **assets/ddd-examples/**: Domain modeling examples
