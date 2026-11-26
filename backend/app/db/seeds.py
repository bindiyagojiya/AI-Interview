"""Seed data for InterviewIQ AI Question Bank"""

DEFAULT_QUESTIONS = [
    # --- Technical: Python ---
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
        "difficulty": "Intermediate",
        "question_text": "What is the Global Interpreter Lock (GIL) in CPython and how does it affect multithreaded CPU-bound tasks?",
        "reference_answer": "The GIL is a mutex that prevents multiple native OS threads from executing Python bytecodes simultaneously in CPython. While it simplifies memory management and keeps thread-safe C extensions fast, it restricts CPU-bound multithreaded Python code to a single CPU core. Developers bypass the GIL using multiprocessing or asynchronous programming for I/O tasks.",
        "key_concepts": ["mutex", "single core", "multiprocessing", "thread-safe", "CPU-bound"]
    },

    # --- Technical: SQL & Databases ---
    {
        "category": "Technical",
        "domain": "SQL",
        "difficulty": "Fresher",
        "question_text": "What is the difference between INNER JOIN and LEFT JOIN in SQL?",
        "reference_answer": "An INNER JOIN returns only the rows that have matching values in both joined tables. A LEFT JOIN returns all rows from the left table along with matched rows from the right table; if no match exists on the right side, NULL values are returned for the right table columns.",
        "key_concepts": ["matching values", "left table", "NULL values", "INNER JOIN", "LEFT JOIN"]
    },
    {
        "category": "Technical",
        "domain": "SQL",
        "difficulty": "Intermediate",
        "question_text": "Explain database indexing, B-Trees, and how indexing affects read versus write performance.",
        "reference_answer": "A database index is a data structure (typically a balanced B-Tree) that improves data retrieval speed from O(N) full table scans to O(log N) tree lookups. However, every INSERT, UPDATE, and DELETE requires updating index trees, which adds write overhead and consumes additional storage space.",
        "key_concepts": ["B-Tree", "O(log N)", "full table scan", "write overhead", "storage"]
    },

    # --- Technical: Data Structures & Algorithms ---
    {
        "category": "Technical",
        "domain": "DSA",
        "difficulty": "Fresher",
        "question_text": "Explain the difference between an Array and a Linked List in terms of memory layout and time complexity for insertion.",
        "reference_answer": "An array stores elements in contiguous memory locations, allowing O(1) random access by index, but insertion at the beginning or middle requires shifting elements with O(n) time. A linked list stores nodes in non-contiguous memory connected by pointers; insertion at the head or where a pointer is known is O(1), but accessing an element by index requires O(n) sequential traversal.",
        "key_concepts": ["contiguous memory", "pointers", "O(1) access", "O(n) insertion", "dynamic size"]
    },
    {
        "category": "Technical",
        "domain": "DSA",
        "difficulty": "Intermediate",
        "question_text": "What is the difference between Breadth-First Search (BFS) and Depth-First Search (DFS), and which data structures are used for each?",
        "reference_answer": "BFS explores a graph level by level and uses a FIFO Queue, making it optimal for finding the shortest path in unweighted graphs. DFS explores as deep as possible along each branch before backtracking and uses a LIFO Stack (or recursion call stack), which is ideal for cycle detection, topological sorting, and maze exploration.",
        "key_concepts": ["Queue", "Stack", "level by level", "backtracking", "shortest path"]
    },

    # --- HR & Behavioral Questions ---
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
        "question_text": "Describe a situation where you had a disagreement with a team member. How did you handle it?",
        "reference_answer": "During a team capstone project, a peer wanted to build our database without foreign key constraints to save development time. Instead of arguing, I scheduled a 15-minute call, showed documentation demonstrating how lack of constraints leads to orphaned records and corrupt analytics, and suggested automated migration scripts to ease development. We aligned peacefully on best practices.",
        "key_concepts": ["conflict resolution", "objective data", "active listening", "compromise", "empathy"]
    }
]

