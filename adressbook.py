from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain 10 digits")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = Phone(new_phone).value
                return
        raise ValueError("Phone number not found")

    def add_birthday(self, date):
        self.birthday = Birthday(date)

    def __str__(self):
        phones = ", ".join(p.value for p in self.phones)
        birthday = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"{self.name.value}: {phones}{birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        result = []

        for record in self.data.values():
            if not record.birthday:
                continue

            birth = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            congratulation = birth.replace(year=today.year)

            if congratulation < today:
                congratulation = congratulation.replace(year=today.year + 1)

            if congratulation.weekday() == 5:
                congratulation += timedelta(days=2)
            elif congratulation.weekday() == 6:
                congratulation += timedelta(days=1)

            if 0 <= (congratulation - today).days <= 7:
                result.append({
                    "name": record.name.value,
                    "birthday": congratulation.strftime("%d.%m.%Y")
                })

        return result


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Not enough arguments provided"
        except AttributeError:
            return "Contact not found"
    return wrapper


@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)

    if record is None:
        record = Record(name)
        book.add_record(record)

    record.add_phone(phone)
    return "Contact saved"


@input_error
def change_phone(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Phone updated"


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    return ", ".join(p.value for p in record.phones)


@input_error
def add_birthday(args, book):
    name, date = args
    record = book.find(name)
    record.add_birthday(date)
    return "Birthday added"


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    return record.birthday.value


@input_error
def birthdays(args, book):
    items = book.get_upcoming_birthdays()
    if not items:
        return "No birthdays in the next 7 days"
    return "\n".join(f"{i['name']}: {i['birthday']}" for i in items)


def parse_input(text):
    return text.strip().split()


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input(">>> ")
        command, *args = parse_input(user_input.lower())

        if command in ("exit", "close"):
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_phone(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            for record in book.values():
                print(record)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command")


if __name__ == "__main__":
    main()
