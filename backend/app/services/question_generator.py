"""
InterviewIQ AI — Role & Difficulty-Aware Question Generator Service
Supports:
1. Curated Multi-Tier Knowledge Bank (Python, React/JS, Java, SQL, Data Science, DevOps, DSA, HR across Fresher/Intermediate/Advanced)
2. Live Gemini LLM Generation via REST API (when GEMINI_API_KEY is configured)
3. Algorithmic Domain Synthesizer for custom/niche roles
"""

import json
import logging
import re
import httpx
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.question import Question
from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Comprehensive Multi-Domain Question Bank (Categorized by Role & Difficulty)
# ---------------------------------------------------------------------------

KNOWLEDGE_BANK: List[Dict[str, Any]] = [
    # =========================================================================
    # PYTHON / BACKEND
    # =========================================================================
    {
        "category": "Technical",
        "domain": "Python",
        "difficulty": "Fresher",
        "question_text": "What are Python list comprehensions and what advantages do they provide over traditional loops?",
        "reference_answer": "List comprehensions provide a concise and readable syntax for creating new lists from existing iterables. They are syntactically cleaner than standard for-loops with append, and they execute faster in CPython because the loop and list construction occur in optimized C code.",
        "key_concepts": ["concise syntax", "iterable", "performance", "readability", "for loop"]
    },
    {
        "category": "Technical",
        "domain": "Python",
        "difficulty": "Fresher",
        "question_text": "Explain the difference between mutable and immutable data types in Python with examples.",
        "reference_answer": "Mutable objects can be modified after creation without changing their memory address, such as lists, dictionaries, and sets. Immutable objects cannot be altered once created; any modification produces a new object in memory, such as integers, floats, strings, and tuples.",
        "key_concepts": ["mutable", "immutable", "memory address", "list", "tuple", "dictionary"]
    },
    {
        "category": "Technical",
        "domain": "Python",
        "difficulty": "Fresher",
        "question_text": "What are Python generators and how does the 'yield' keyword differ from 'return'?",
        "reference_answer": "Generators are functions that produce an iterable sequence lazily using the 'yield' keyword. Unlike 'return', which terminates the function and returns a complete collection into memory, 'yield' pauses function execution, saves state, and emits items on demand, drastically conserving memory.",
        "key_concepts": ["generator", "yield", "lazy evaluation", "memory efficiency", "state suspension"]
    },
    {
        "category": "Technical",
        "domain": "Python",
        "difficulty": "Intermediate",
        "question_text": "What is the Global Interpreter Lock (GIL) in CPython and how does it affect multithreaded CPU-bound tasks?",
        "reference_answer": "The GIL is a mutex that prevents multiple native OS threads from executing Python bytecodes simultaneously in CPython. While it simplifies memory management and keeps thread-safe C extensions fast, it restricts CPU-bound multithreaded Python code to a single CPU core. Developers bypass the GIL using multiprocessing or asynchronous programming for I/O tasks.",
        "key_concepts": ["mutex", "single core", "multiprocessing", "thread-safe", "CPU-bound"]
    },
    {
        "category": "Technical",
        "domain": "Python",
        "difficulty": "Intermediate",
        "question_text": "Explain Python decorators, how closures work behind them, and give a practical use case.",
        "reference_answer": "A decorator is a callable that takes another function as an argument, extends its behavior without modifying the original code, and returns a modified function. Decorators rely on closures to capture the wrapped function and arguments. Common use cases include logging, authentication, timing, and rate limiting.",
        "key_concepts": ["decorator", "closure", "higher-order function", "wrapper", "metadata"]
    },
    {
        "category": "Technical",
        "domain": "Python",
        "difficulty": "Advanced",
        "question_text": "How does CPython's cyclic garbage collector detect and collect circular references, and how do generational heuristics work?",
        "reference_answer": "CPython uses reference counting as its primary memory mechanism, immediately freeing objects when count hits 0. To resolve cyclic references where objects reference each other, it uses a cycle detection algorithm operating across 3 generational lists (Gen 0, 1, 2). Objects that survive garbage collection cycles are promoted to older generations which are collected less frequently.",
        "key_concepts": ["cyclic garbage collection", "reference counting", "generations", "Gen 0 Gen 1 Gen 2", "gc module", "memory leak"]
    },
    {
        "category": "Technical",
        "domain": "Python",
        "difficulty": "Advanced",
        "question_text": "Explain the Python asyncio event loop architecture, coroutines, and how cooperative multitasking handles thousands of concurrent I/O connections.",
        "reference_answer": "asyncio runs on a single-threaded cooperative event loop using non-blocking OS primitives like epoll or kqueue. When a coroutine hits an 'await', it yields execution back to the loop, allowing other ready tasks to execute. Because tasks switch cooperatively without OS thread context switches, it scales to tens of thousands of concurrent connections.",
        "key_concepts": ["event loop", "coroutine", "cooperative multitasking", "non-blocking IO", "epoll", "async await"]
    },

    # =========================================================================
    # JAVASCRIPT / REACT / FRONTEND / MOBILE
    # =========================================================================
    {
        "category": "Technical",
        "domain": "React",
        "difficulty": "Fresher",
        "question_text": "What is the Virtual DOM in React and how does reconciliation improve UI rendering performance?",
        "reference_answer": "The Virtual DOM is an in-memory lightweight representation of the real DOM. When state changes, React creates a new virtual DOM tree, diffs it with the previous tree using a heuristic reconciliation algorithm, and computes the minimal set of real DOM operations required, avoiding expensive direct DOM manipulations.",
        "key_concepts": ["Virtual DOM", "reconciliation", "diffing algorithm", "real DOM overhead", "minimal updates"]
    },
    {
        "category": "Technical",
        "domain": "React",
        "difficulty": "Fresher",
        "question_text": "Explain the difference between state and props in React, and when you should use each.",
        "reference_answer": "Props (properties) are read-only inputs passed from parent to child components to configure behavior and render content. State represents mutable local data managed directly within a component that dictates its dynamic behavior and triggers re-renders when updated via setState.",
        "key_concepts": ["state", "props", "immutability", "unidirectional data flow", "re-render"]
    },
    {
        "category": "Technical",
        "domain": "React",
        "difficulty": "Intermediate",
        "question_text": "Explain the dependencies array in useEffect, how closures can cause stale state bugs, and how to prevent unnecessary re-executions.",
        "reference_answer": "The useEffect dependency array specifies values that trigger the effect on change. An empty array runs once on mount. If a callback inside useEffect captures state without declaring it in dependencies, it forms a closure over stale state. Developers fix this using functional state updates (setVal(prev => prev + 1)) or useCallback/useRef.",
        "key_concepts": ["useEffect", "dependency array", "stale closures", "cleanup function", "functional updates"]
    },
    {
        "category": "Technical",
        "domain": "React",
        "difficulty": "Intermediate",
        "question_text": "Compare React Context API with Redux for state management. When is Context sufficient, and when is Redux preferred?",
        "reference_answer": "Context API is built into React and is ideal for low-frequency global data like theme, authenticated user, and localization. However, any context change re-renders all consumers. Redux provides fine-grained selector subscriptions, predictable action/reducer workflows, middleware for side effects, and time-travel debugging for complex, high-frequency state updates.",
        "key_concepts": ["Context API", "Redux", "re-render optimization", "selectors", "middleware", "predictable state"]
    },
    {
        "category": "Technical",
        "domain": "React",
        "difficulty": "Advanced",
        "question_text": "How does React Fiber architecture enable incremental rendering, and how does concurrent mode prioritize user interactions over heavy background work?",
        "reference_answer": "React Fiber replaced the recursive call stack with a singly-linked list of fiber nodes, breaking render work into small units. Under Concurrent React, the engine can pause, abort, or prioritize work based on deadlines (using MessageChannel / requestIdleCallback). High-priority user inputs (clicks, keystrokes) interrupt low-priority transitions.",
        "key_concepts": ["Fiber", "concurrent rendering", "time-slicing", "work prioritizing", "interruptible rendering", "useTransition"]
    },
    {
        "category": "Technical",
        "domain": "React",
        "difficulty": "Advanced",
        "question_text": "Explain critical rendering path optimization, Code Splitting with dynamic imports, and how to diagnose memory leaks caused by detached DOM nodes in Single Page Applications.",
        "reference_answer": "Code splitting uses dynamic import() and React.lazy to serve chunks on demand, reducing initial bundle size. Detached DOM nodes occur when UI elements are removed from the DOM but lingering JavaScript references (event listeners, timers, closures) retain them in memory. Diagnosing involves Chrome DevTools Heap Snapshots and allocation timelines.",
        "key_concepts": ["code splitting", "dynamic imports", "detached DOM nodes", "heap snapshots", "memory leak", "critical path"]
    },

    # =========================================================================
    # JAVA / SPRING BOOT
    # =========================================================================
    {
        "category": "Technical",
        "domain": "Java",
        "difficulty": "Fresher",
        "question_text": "What is the difference between JVM, JRE, and JDK, and why is Java called platform-independent?",
        "reference_answer": "JDK is the development kit containing compiler (javac) and tools. JRE contains the runtime libraries to run applications. JVM is the engine that executes compiled bytecode. Java is platform-independent because source code compiles into platform-neutral bytecode that runs on any OS having a compatible JVM.",
        "key_concepts": ["JDK", "JRE", "JVM", "bytecode", "platform independence", "WORA"]
    },
    {
        "category": "Technical",
        "domain": "Java",
        "difficulty": "Fresher",
        "question_text": "Explain String immutability in Java and how the String Constant Pool optimizes heap memory usage.",
        "reference_answer": "In Java, String objects are immutable; their character values cannot be changed after creation. The JVM maintains a String Constant Pool inside heap memory. When a string literal is created, the JVM checks the pool: if it exists, the reference is shared; otherwise, a single copy is cached, reducing memory overhead and ensuring security.",
        "key_concepts": ["immutability", "String Constant Pool", "heap memory", "thread safety", "caching"]
    },
    {
        "category": "Technical",
        "domain": "Java",
        "difficulty": "Intermediate",
        "question_text": "Explain Spring Boot Dependency Injection, Inversion of Control (IoC), and the lifecycle of a Spring Bean.",
        "reference_answer": "IoC delegates object creation and dependency management to the Spring ApplicationContext. Dependency Injection provides dependencies via constructors, setters, or @Autowired fields. Bean lifecycle progresses through: instantiation, property population, BeanPostProcessors (postProcessBeforeInitialization), @PostConstruct/init-method, ready for use, and @PreDestroy on shutdown.",
        "key_concepts": ["Dependency Injection", "Inversion of Control", "ApplicationContext", "Bean lifecycle", "PostConstruct"]
    },
    {
        "category": "Technical",
        "domain": "Java",
        "difficulty": "Intermediate",
        "question_text": "What is the N+1 select problem in Hibernate/JPA and what are the standard strategies to resolve it?",
        "reference_answer": "The N+1 problem occurs when fetching 1 parent entity results in N additional database queries to fetch related child entities due to lazy loading. It is resolved using JOIN FETCH in JPQL, @EntityGraph to specify fetch plans, or configuring batch fetching (@BatchSize) to load children in batches.",
        "key_concepts": ["N+1 problem", "JOIN FETCH", "EntityGraph", "lazy loading", "BatchSize", "ORM optimization"]
    },
    {
        "category": "Technical",
        "domain": "Java",
        "difficulty": "Advanced",
        "question_text": "Explain Java's Project Loom Virtual Threads, how they differ from OS platform threads, and their impact on high-throughput server architecture.",
        "reference_answer": "Platform threads map 1:1 to OS kernel threads, consuming around 1MB stack memory and incurring high context-switching costs. Virtual threads are lightweight user-mode threads managed by the JVM, mounted on carrier platform threads. When a virtual thread blocks on I/O, it unmounts from its carrier thread, allowing millions of concurrent requests with standard synchronous programming models.",
        "key_concepts": ["Virtual Threads", "Project Loom", "carrier threads", "context switching", "high throughput", "blocking IO"]
    },
    {
        "category": "Technical",
        "domain": "Java",
        "difficulty": "Advanced",
        "question_text": "How do distributed transactions work in microservices, and why is the Saga pattern preferred over Two-Phase Commit (2PC)?",
        "reference_answer": "2PC requires a centralized coordinator locking resources across all participating services until all agree to commit, causing high latency and vulnerability to coordinator failure. The Saga pattern breaks a distributed transaction into a sequence of local transactions coordinated via choreographing events or an orchestrator, handling failures through compensating rollback transactions.",
        "key_concepts": ["Saga pattern", "Two-Phase Commit", "compensating transactions", "orchestration", "choreography", "eventual consistency"]
    },

    # =========================================================================
    # SQL & DATABASES
    # =========================================================================
    {
        "category": "Technical",
        "domain": "SQL",
        "difficulty": "Fresher",
        "question_text": "What is the difference between INNER JOIN and LEFT JOIN in SQL?",
        "reference_answer": "An INNER JOIN returns only rows with matching keys in both tables. A LEFT JOIN returns all rows from the left table and matched rows from the right; unmatched right rows contain NULL values.",
        "key_concepts": ["matching values", "left table", "NULL values", "INNER JOIN", "LEFT JOIN"]
    },
    {
        "category": "Technical",
        "domain": "SQL",
        "difficulty": "Fresher",
        "question_text": "Explain Database Normalization and the requirements for First, Second, and Third Normal Forms (1NF, 2NF, 3NF).",
        "reference_answer": "Normalization organizes database tables to reduce redundancy and anomalies. 1NF requires atomic values and unique records. 2NF removes partial functional dependencies on composite keys. 3NF removes transitive dependencies where non-key attributes depend on other non-key attributes.",
        "key_concepts": ["normalization", "redundancy", "1NF atomic", "2NF partial dependency", "3NF transitive dependency"]
    },
    {
        "category": "Technical",
        "domain": "SQL",
        "difficulty": "Intermediate",
        "question_text": "Explain database indexing, B-Trees, and how indexing affects read versus write performance.",
        "reference_answer": "An index is a balanced B-Tree structure enabling O(log N) lookups instead of O(N) full table scans. While indexes speed up SELECT queries, they introduce write latency because INSERT, UPDATE, and DELETE operations must update index trees and consume additional storage.",
        "key_concepts": ["B-Tree", "O(log N)", "full table scan", "write overhead", "storage"]
    },
    {
        "category": "Technical",
        "domain": "SQL",
        "difficulty": "Intermediate",
        "question_text": "Explain ACID properties in database transactions and how Isolation Levels prevent concurrency anomalies like dirty reads and phantom reads.",
        "reference_answer": "ACID ensures Atomicity (all or nothing), Consistency (valid state transitions), Isolation (concurrency control), and Durability (persistence on disk). Isolation levels (Read Uncommitted, Read Committed, Repeatable Read, Serializable) progressively prevent Dirty Reads, Non-Repeatable Reads, and Phantom Reads using locks or Multi-Version Concurrency Control (MVCC).",
        "key_concepts": ["ACID", "isolation levels", "dirty read", "phantom read", "MVCC", "transactions"]
    },
    {
        "category": "Technical",
        "domain": "SQL",
        "difficulty": "Advanced",
        "question_text": "How does Multi-Version Concurrency Control (MVCC) operate in PostgreSQL, and how does VACUUM handle dead tuple reclamation?",
        "reference_answer": "PostgreSQL MVCC ensures readers do not block writers and writers do not block readers by creating a new row version (tuple) with xmin/xmax transaction IDs on UPDATE or DELETE. Old versions remain visible to concurrent transactions until completed. VACUUM scans table pages, identifies dead tuples whose transactions have ended, frees the space for reuse, and updates visibility maps.",
        "key_concepts": ["MVCC", "dead tuples", "xmin xmax", "VACUUM", "autovacuum", "table bloat"]
    },

    # =========================================================================
    # DATA SCIENCE & MACHINE LEARNING
    # =========================================================================
    {
        "category": "Technical",
        "domain": "Data Science",
        "difficulty": "Fresher",
        "question_text": "Explain the Bias-Variance tradeoff in Machine Learning and how it relates to underfitting and overfitting.",
        "reference_answer": "Bias is error caused by overly simplistic assumptions, leading to underfitting where the model misses patterns in training data. Variance is sensitivity to small fluctuations in training data, causing overfitting where the model memorizes noise and fails to generalize. The goal is to find the sweet spot minimizing total error.",
        "key_concepts": ["bias", "variance", "underfitting", "overfitting", "generalization"]
    },
    {
        "category": "Technical",
        "domain": "Data Science",
        "difficulty": "Fresher",
        "question_text": "What is the difference between Precision and Recall, and when would you optimize for Recall over Precision?",
        "reference_answer": "Precision is true positives divided by all predicted positives (accuracy of positive predictions). Recall is true positives divided by all actual positives (ability to find all true cases). You optimize for Recall in high-risk detection like medical diagnosis or fraud, where a false negative is far worse than a false positive.",
        "key_concepts": ["precision", "recall", "true positives", "false negatives", "F1 score"]
    },
    {
        "category": "Technical",
        "domain": "Data Science",
        "difficulty": "Intermediate",
        "question_text": "Compare Random Forests with Gradient Boosting Machines (e.g. XGBoost/LightGBM). How do their tree building techniques differ?",
        "reference_answer": "Random Forest is a bagging ensemble that builds independent deep decision trees in parallel using bootstrapped data and random feature subsets, reducing variance by averaging. Gradient Boosting builds shallow trees sequentially, where each new tree is trained to predict the residual errors (gradient) of previous trees, reducing bias.",
        "key_concepts": ["Random Forest", "Gradient Boosting", "bagging", "boosting", "residual error", "XGBoost"]
    },
    {
        "category": "Technical",
        "domain": "Data Science",
        "difficulty": "Advanced",
        "question_text": "Explain the Multi-Head Self-Attention mechanism in Transformer models and why it scales better than recurrent architectures like LSTMs.",
        "reference_answer": "Self-attention computes attention weights between every pair of tokens in a sequence using Query, Key, and Value matrix multiplications: Softmax(QK^T / sqrt(d_k)) * V. Unlike LSTMs which process tokens sequentially with O(N) sequential steps and suffer vanishing gradients, Transformers process entire sequences in parallel across multiple attention heads, capturing long-range dependencies efficiently.",
        "key_concepts": ["Self-Attention", "Query Key Value", "parallelization", "Transformer", "vanishing gradient", "Softmax"]
    },

    # =========================================================================
    # DEVOPS / CLOUD / SYSTEM ARCHITECTURE
    # =========================================================================
    {
        "category": "Technical",
        "domain": "DevOps",
        "difficulty": "Fresher",
        "question_text": "What is the difference between Docker containers and Virtual Machines in terms of architecture and resource overhead?",
        "reference_answer": "Virtual Machines run a complete guest OS on top of a hypervisor with dedicated virtual hardware, making them heavy with slow boot times. Containers share the host kernel and isolate processes using Linux namespaces and cgroups, making them lightweight, fast to start, and resource-efficient.",
        "key_concepts": ["Docker container", "Virtual Machine", "shared host kernel", "namespaces", "cgroups", "hypervisor"]
    },
    {
        "category": "Technical",
        "domain": "DevOps",
        "difficulty": "Intermediate",
        "question_text": "Explain Kubernetes Pods, Deployments, and Services, and how traffic reaches an application through an Ingress controller.",
        "reference_answer": "A Pod is the smallest deployable unit running one or more containers. A Deployment manages Pod replicas, rolling updates, and self-healing. A Service provides a stable internal IP and load balancing across dynamic pods. An Ingress controller acts as an application layer (L7) reverse proxy routing external HTTPS traffic to matching backend services.",
        "key_concepts": ["Kubernetes Pod", "Deployment", "Service", "Ingress controller", "rolling update", "load balancing"]
    },
    {
        "category": "Technical",
        "domain": "DevOps",
        "difficulty": "Advanced",
        "question_text": "How do you design a zero-downtime database schema migration strategy in a distributed high-traffic system?",
        "reference_answer": "Use the Expand and Contract pattern across distinct deployment phases: 1) Expand: Add new nullable columns or tables without breaking existing app versions. 2) Dual-write: Deploy app code that writes to both old and new schema. 3) Backfill: Migrate historical data asynchronously. 4) Switch reads: Direct traffic to the new schema. 5) Contract: Remove old schema columns once verified.",
        "key_concepts": ["zero downtime", "expand contract", "backward compatibility", "dual write", "backfilling"]
    },

    # =========================================================================
    # HR & BEHAVIORAL QUESTIONS
    # =========================================================================
    {
        "category": "HR",
        "domain": "Behavioral",
        "difficulty": "Fresher",
        "question_text": "Tell me about a challenging project or technical problem you worked on and how you resolved it.",
        "reference_answer": "In a college database project, our query execution time became too slow with large datasets. I used the STAR method: identified missing indexes on foreign keys, benchmarked queries with EXPLAIN, added composite B-Tree indexes, and reduced query latency by 75%. I learned the importance of profiling before optimizing.",
        "key_concepts": ["STAR method", "situation", "task", "action", "result", "collaboration", "learning"]
    },
    {
        "category": "HR",
        "domain": "Behavioral",
        "difficulty": "Fresher",
        "question_text": "Why do you want to work for our organization and what makes you a strong candidate?",
        "reference_answer": "I admire your company's focus on scalable engineering practices and continuous innovation. As a disciplined graduate with hands-on project experience in full-stack architecture, database design, and algorithmic problem-solving, I combine technical competence with rapid learning ability and strong team communication.",
        "key_concepts": ["alignment", "engineering practices", "hands-on experience", "continuous learning", "team player"]
    },
    {
        "category": "HR",
        "domain": "Behavioral",
        "difficulty": "Intermediate",
        "question_text": "Describe a situation where you had a disagreement with a team member or stakeholder on technical direction. How did you handle it?",
        "reference_answer": "During a team capstone project, a peer wanted to build our database without foreign key constraints to save development time. Instead of arguing, I scheduled a 15-minute call, showed documentation demonstrating how lack of constraints leads to orphaned records and corrupt analytics, and suggested automated migration scripts to ease development. We aligned peacefully on best practices.",
        "key_concepts": ["conflict resolution", "objective data", "active listening", "compromise", "empathy"]
    },
    {
        "category": "HR",
        "domain": "Behavioral",
        "difficulty": "Intermediate",
        "question_text": "Tell me about a time when a software release or feature failed in testing or production. How did you respond?",
        "reference_answer": "During a sprint deployment, an unhandled null pointer caused our authentication service to fail. I initiated incident response: rolled back to the prior stable artifact, checked cloud logs to isolate the missing attribute, patched the code with null-safety checks and added regression unit tests, and wrote a post-mortem to prevent recurrence.",
        "key_concepts": ["incident response", "rollback", "post-mortem", "root cause analysis", "calm under pressure"]
    },
    {
        "category": "HR",
        "domain": "Behavioral",
        "difficulty": "Advanced",
        "question_text": "Describe how you make high-stakes architectural decisions with incomplete information, and how you align cross-functional engineering teams.",
        "reference_answer": "When facing architectural uncertainty, I write an Architectural Decision Record (ADR) analyzing trade-offs, scalability constraints, and failure modes. I build rapid proof-of-concept benchmarks to gather empirical data, consult senior staff across teams, establish a two-way door decision mindset so we can pivot if needed, and communicate rationale clearly to stakeholders.",
        "key_concepts": ["Architectural Decision Record", "trade-off analysis", "stakeholder alignment", "empirical data", "leadership", "risk mitigation"]
    },
    {
        "category": "HR",
        "domain": "Behavioral",
        "difficulty": "Advanced",
        "question_text": "How do you manage engineering technical debt against rapid product feature delivery expectations?",
        "reference_answer": "I don't treat technical debt as an abstract complaint; I quantify its cost in terms of developer velocity, customer incident rates, and cloud spend. I negotiate a dedicated 20% capacity allocation in every sprint for debt reduction, prioritize items that unlock future business features, and implement automated quality gates in CI/CD to prevent new debt from entering.",
        "key_concepts": ["technical debt", "quantifiable metrics", "sprint capacity", "velocity", "stakeholder negotiation", "engineering excellence"]
    }
]

# ---------------------------------------------------------------------------
# Helper: Domain Normalizer
# ---------------------------------------------------------------------------

def normalize_domain(target_role: str, interview_type: str) -> str:
    """Maps free-text role to primary technology domain using word boundaries."""
    if "hr" in interview_type.lower() or "behav" in interview_type.lower():
        return "Behavioral"

    role_lower = target_role.lower()

    def has_token(patterns):
        for pat in patterns:
            if re.search(r'\b' + re.escape(pat) + r'\b', role_lower):
                return True
        return False

    if has_token(["python", "django", "flask", "fastapi"]):
        return "Python"
    if has_token(["react", "javascript", "frontend", "web", "node", "typescript", "vue", "angular", "mobile", "android", "ios", "react native"]):
        return "React"
    if has_token(["java", "spring", "springboot", "enterprise"]):
        return "Java"
    if has_token(["sql", "database", "dba", "postgres", "mysql"]):
        return "SQL"
    if has_token(["data science", "machine learning", "deep learning", "ai", "ml", "ai engineer", "data analyst", "data engineer", "nlp", "computer vision"]):
        return "Data Science"
    if has_token(["devops", "cloud", "sre", "aws", "docker", "kubernetes", "infra", "infrastructure"]):
        return "DevOps"
    return target_role.strip().title()

# ---------------------------------------------------------------------------
# Dynamic AI Synthesizer (Fallback when Gemini is not configured or offline)
# ---------------------------------------------------------------------------

def synthesize_custom_role_questions(target_role: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
    """Synthesizes high-quality tailored questions for any specific role and difficulty level."""
    diff_lower = difficulty.lower()
    
    if "fresher" in diff_lower:
        templates = [
            (
                f"What are the foundational architectural principles of {target_role}, and what core problem does it solve in modern software development?",
                f"For a {target_role}, fundamental principles include modularity, separation of concerns, and clean lifecycle management. It enables developers to build maintainable, decoupled systems with clear interfaces and predictable behavior.",
                ["modularity", "lifecycle management", "separation of concerns", "fundamentals"]
            ),
            (
                f"In your work as a {target_role}, how do you structure error handling and input validation to maintain application stability?",
                f"Robust error handling in {target_role} involves graceful exception handling, validating user inputs at boundaries, using structured logging, and returning clean error messages without exposing sensitive stack traces.",
                ["error handling", "input validation", "structured logging", "graceful failure"]
            ),
            (
                f"Explain the primary tools, build processes, and testing methodologies essential for an entry-level {target_role}.",
                f"An entry-level {target_role} must be proficient in version control (Git), local build and package managers, unit testing frameworks, and adhering to standard coding style guidelines and code reviews.",
                ["version control", "unit testing", "build pipeline", "debugging"]
            ),
            (
                f"What is the difference between synchronous and asynchronous operations in the context of {target_role}?",
                f"Synchronous execution blocks subsequent code until the current task completes, whereas asynchronous execution initiates tasks and handles completion via callbacks, promises, or event loops without freezing the main thread.",
                ["synchronous", "asynchronous", "non-blocking", "event loop", "responsiveness"]
            ),
            (
                f"How do you organize data structures and manage memory efficiency when implementing features in {target_role}?",
                f"Managing memory in {target_role} requires selecting optimal data structures based on time/space complexity, avoiding memory leaks from unclosed resources, and profiling memory usage under load.",
                ["data structures", "space complexity", "resource cleanup", "memory optimization"]
            )
        ]
    elif "intermediate" in diff_lower:
        templates = [
            (
                f"How do you handle state consistency, caching, and network latency optimization as an experienced {target_role}?",
                f"As an intermediate {target_role}, optimizing latency requires using distributed caching (Redis/Memcached), implementing cache invalidation strategies (Cache-Aside), and ensuring eventual consistency across state updates.",
                ["caching", "cache invalidation", "latency optimization", "state consistency", "Redis"]
            ),
            (
                f"Describe common performance bottlenecks encountered in {target_role} applications and your methodical approach to profiling and resolving them.",
                f"Bottlenecks typically stem from inefficient queries, excessive re-renders, thread contention, or blocking I/O. Profiling using telemetry, metrics, and CPU/memory heap profilers helps isolate root causes before applying algorithmic fixes.",
                ["profiling", "bottlenecks", "telemetry", "heap analysis", "algorithmic optimization"]
            ),
            (
                f"Explain how design patterns (e.g. Factory, Observer, Singleton, or Strategy) are practically applied in {target_role} codebases.",
                f"Design patterns provide reusable templates for common architectural problems in {target_role}. For example, the Strategy pattern isolates interchangeable algorithms, while Observer/Pub-Sub decouples event producers from consumers.",
                ["design patterns", "Strategy pattern", "Observer", "decoupling", "extensibility"]
            ),
            (
                f"How do you secure {target_role} systems against vulnerabilities like injection attacks, unauthorized access, and sensitive data leakage?",
                f"Security requires defense in depth: parameterized queries against injection, strict role-based access control (RBAC), TLS encryption in transit and AES at rest, and validating API tokens via secure headers.",
                ["defense in depth", "RBAC", "parameterized queries", "encryption", "token validation"]
            ),
            (
                f"Describe your strategy for writing maintainable integration tests and mock services in a {target_role} CI/CD workflow.",
                f"Maintainable testing balances fast unit tests with isolated integration tests using mock servers or containerized test databases (Testcontainers), integrated into automated CI/CD pull request validation pipelines.",
                ["integration testing", "mocking", "CI/CD", "automated pipelines", "test coverage"]
            )
        ]
    else:  # Advanced
        templates = [
            (
                f"How do you architect a high-throughput, horizontally scalable distributed system for {target_role} supporting 99.99% availability?",
                f"At an advanced level, architecting for {target_role} involves stateless services behind load balancers, database sharding/read-replicas, asynchronous event-driven queues (Kafka), circuit breakers (Resilience4j), and graceful degradation strategies under load.",
                ["horizontal scalability", "event-driven", "circuit breaker", "high availability", "sharding", "fault tolerance"]
            ),
            (
                f"Explain how you manage concurrency control, race conditions, and distributed locking in high-volume {target_role} deployments.",
                f"Handling concurrency at scale requires optimistic locking with version fields for low contention, distributed locking (Redlock / ZooKeeper) for critical shared resources, and idempotency keys to safely retry failed requests.",
                ["distributed locking", "concurrency control", "race conditions", "optimistic locking", "idempotency"]
            ),
            (
                f"Describe your methodology for conducting architectural reviews and refactoring legacy monolithic codebases into modern {target_role} microservices.",
                f"Migrating legacy systems uses the Strangler Fig pattern to incrementally replace monolithic components with bounded-context microservices, establishing API gateways, event contracts, and distributed tracing (OpenTelemetry).",
                ["Strangler Fig pattern", "microservices", "bounded context", "distributed tracing", "API gateway"]
            ),
            (
                f"How do you design disaster recovery, multi-region failover, and ensure data integrity (RPO and RTO) for mission-critical {target_role} workloads?",
                f"Disaster recovery requires establishing strict RTO and RPO targets, deploying active-active or active-passive multi-region cloud topology with automated DNS failover, continuous database replication, and regular chaos engineering drills.",
                ["RTO RPO", "disaster recovery", "multi-region failover", "replication", "chaos engineering"]
            ),
            (
                f"What trade-offs do you navigate between immediate business delivery and long-term architectural scalability when leading technical strategy as a senior {target_role}?",
                f"Senior leadership balances velocity with technical health by defining explicit Service Level Objectives (SLOs), budgeting technical debt mitigation within sprints, and ensuring core architectural abstractions remain modular for future scale.",
                ["SLOs", "trade-off analysis", "technical strategy", "modularity", "scalability"]
            )
        ]

    results = []
    for q_text, ref_ans, concepts in templates[:count]:
        results.append({
            "category": "Technical",
            "domain": target_role,
            "difficulty": difficulty,
            "question_text": q_text,
            "reference_answer": ref_ans,
            "key_concepts": concepts
        })
    return results

# ---------------------------------------------------------------------------
# Gemini LLM Dynamic Generator
# ---------------------------------------------------------------------------

def generate_via_gemini(target_role: str, difficulty: str, interview_type: str, count: int) -> List[Dict[str, Any]]:
    """Calls Gemini REST API to dynamically generate authentic, custom questions."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return []

    prompt = f"""
You are an expert technical interviewer and hiring manager.
Generate {count} unique interview questions for a candidate applying for the role '{target_role}'.
Interview Type: {interview_type}
Experience Level: {difficulty} (e.g. Fresher = fundamentals & syntax, Intermediate = real-world & trade-offs, Advanced = system design, scalability & deep internals).

Return ONLY a valid JSON array of objects with no markdown code fences and no extra text.
Each object must have exactly these keys:
- "question_text": The clear, articulate interview question.
- "reference_answer": A comprehensive, model answer (3-5 sentences) demonstrating strong competence.
- "key_concepts": A list of 4-6 essential technical keywords or concepts required in an ideal response.
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 2048}
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text_content = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                # Clean any markdown fences
                if text_content.startswith("```json"):
                    text_content = text_content[7:]
                if text_content.startswith("```"):
                    text_content = text_content[3:]
                if text_content.endswith("```"):
                    text_content = text_content[:-3]
                parsed = json.loads(text_content.strip())
                if isinstance(parsed, list):
                    formatted = []
                    for item in parsed:
                        if "question_text" in item and "reference_answer" in item:
                            formatted.append({
                                "category": interview_type,
                                "domain": target_role,
                                "difficulty": difficulty,
                                "question_text": item["question_text"],
                                "reference_answer": item["reference_answer"],
                                "key_concepts": item.get("key_concepts", [])
                            })
                    return formatted[:count]
    except Exception as e:
        logger.warning(f"Gemini API dynamic question generation skipped: {e}")

    return []

# ---------------------------------------------------------------------------
# Main Orchestrator: Prepare Session Questions
# ---------------------------------------------------------------------------

def prepare_session_questions(
    db: Session,
    interview_type: str,
    target_role: str,
    difficulty: str,
    count: int,
    topics: Optional[str] = None
) -> List[Question]:
    """
    Retrieves or generates exactly `count` tailored questions for the target role and difficulty.
    Saves new questions to the database so they are permanent and searchable.
    """
    type_lower = interview_type.lower()
    if "coding" in type_lower:
        clean_type = "Coding"
    elif "project" in type_lower:
        clean_type = "Project-Based"
    elif "hr" in type_lower or "behav" in type_lower:
        clean_type = "HR"
    else:
        clean_type = "Technical"

    clean_diff = difficulty.capitalize() if difficulty else "Fresher"
    effective_role = f"{target_role} - {topics}" if topics and topics.strip() else target_role
    normalized_domain = normalize_domain(topics if topics and topics.strip() else target_role, clean_type)

    # 1. Search database for existing questions matching Category + Domain + Difficulty
    existing_db_questions = db.query(Question).filter(
        Question.category == clean_type,
        Question.domain == normalized_domain,
        Question.difficulty == clean_diff
    ).all()

    selected_questions: List[Question] = list(existing_db_questions[:count])

    needed_count = count - len(selected_questions)
    if needed_count <= 0:
        return selected_questions

    # 2. Try Gemini LLM Generation first if configured
    new_raw_questions: List[Dict[str, Any]] = []
    if settings.GEMINI_API_KEY:
        new_raw_questions = generate_via_gemini(target_role, clean_diff, clean_type, needed_count)

    # 3. If Gemini didn't return enough, pull from Knowledge Bank
    if len(new_raw_questions) < needed_count:
        bank_matches = [
            q for q in KNOWLEDGE_BANK
            if q["category"].lower() == clean_type.lower()
            and q["domain"].lower() == normalized_domain.lower()
            and q["difficulty"].lower() == clean_diff.lower()
        ]
        # Avoid duplicates with already selected questions
        existing_texts = {q.question_text for q in selected_questions}
        for bq in bank_matches:
            if bq["question_text"] not in existing_texts:
                new_raw_questions.append(bq)
                if len(new_raw_questions) >= needed_count:
                    break

    # 4. If still not enough (e.g. custom/niche role or high count), use Synthesizer
    if len(new_raw_questions) < needed_count:
        still_needed = needed_count - len(new_raw_questions)
        if clean_type == "HR":
            # Fall back to any HR questions in the bank
            hr_extras = [
                q for q in KNOWLEDGE_BANK
                if q["category"] == "HR" and q["question_text"] not in {q.question_text for q in selected_questions}
            ]
            new_raw_questions.extend(hr_extras[:still_needed])
        else:
            synthesized = synthesize_custom_role_questions(target_role, clean_diff, still_needed)
            new_raw_questions.extend(synthesized)

    # 5. Persist newly generated questions into the database
    for raw in new_raw_questions[:needed_count]:
        new_q = Question(
            category=raw.get("category", clean_type),
            domain=raw.get("domain", normalized_domain),
            difficulty=raw.get("difficulty", clean_diff),
            question_text=raw["question_text"],
            reference_answer=raw["reference_answer"],
            key_concepts=raw.get("key_concepts", [])
        )
        db.add(new_q)
        db.commit()
        db.refresh(new_q)
        selected_questions.append(new_q)

    return selected_questions[:count]
