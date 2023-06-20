# if, else, for, range, return, ze struktur list, set, dict, tuple, class, dataclass oraz z list comprehension. 
# Każda instrukcja musi wystąpić co najmniej raz w zad. a lub b.
from dataclasses import dataclass
from typing import Tuple, List, Dict, Set
import random

@dataclass
class Person:
    name: str
    age: int

def generate_persons(num: int) -> list:
    persons = []
    names = ["Alice", "Bob", "Charlie", "David", "Emily"]
    for i in range(num):
        name = random.choice(names)
        age = random.randint(18, 60)
        person = Person(name, age)  
        persons.append(person)
    return persons

def filter_persons_by_age(persons: list, min_age: int) -> list:
    filtered_persons = [person for person in persons if person.age >= min_age]
    return filtered_persons

def count_persons_by_name(persons: list) -> dict:
    name_counts = {}
    for person in persons:
        if person.name in name_counts:
            name_counts[person.name] += 1
        else:
            name_counts[person.name] = 1
    return name_counts

def main():
    persons = generate_persons(10)
    print("Generated persons:")
    for person in persons:
        print(f"{person.name} ({person.age})")

    min_age = 30
    filtered_persons = filter_persons_by_age(persons, min_age)
    print(f"\nFiltered persons with age >= {min_age}:")
    for person in filtered_persons:
        print(f"{person.name} ({person.age})")

    name_counts = count_persons_by_name(persons)
    print("\nName counts:")
    for name, count in name_counts.items():
        print(f"{name}: {count}")

if __name__ == "__main__":
    main()