from dataclasses import dataclass
import random
from src import utils


@dataclass
class Person:
    name: str
    age: int


def generate_persons(num: int) -> list[Person]:
    persons = []
    for _ in range(num):
        name = utils.generate_name()
        age = random.randint(18, 60)
        person = Person(name, age)
        persons.append(person)
    return persons


def filter_persons_by_age(persons: list[Person], min_age: int) -> list[Person]:
    filtered_persons = [person for person in persons if person.age >= min_age]
    return filtered_persons


def count_persons_by_name(persons: list[Person]) -> dict[str, int]:
    name_counts = {}
    for person in persons:
        if person.name in name_counts:
            name_counts[person.name] += 1
        else:
            name_counts[person.name] = 1
    return name_counts


def print_person_info(person: Person) -> None:
    info = tuple((f"Name: {person.name}", f"Age: {person.age}"))
    print(info)


def main():
    persons = generate_persons(10)
    print("Generated persons:")
    for person in persons:
        print_person_info(person)

    min_age = 30
    filtered_persons = filter_persons_by_age(persons, min_age)
    print(f"\nFiltered persons with age >= {min_age}:")
    for person in filtered_persons:
        print_person_info(person)

    name_counts = count_persons_by_name(persons)
    print("\nName counts:")
    for name, count in name_counts.items():
        print("\tName:", name, "Count:", count)


if __name__ == "__main__":
    main()
