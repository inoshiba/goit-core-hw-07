from collections import UserDict
from datetime import datetime, timedelta


class BaseField:
    def __init__(self, value):
        self.value = value


class PersonName(BaseField):
    pass


class PhoneNumber(BaseField):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone must contain 10 digits")
        super().__init__(value)


class BirthDate(BaseField):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)


class ContactRecord:
    def __init__(self, name):
        self.name = PersonName(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(PhoneNumber(phone))

    def change_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = PhoneNumber(new_phone).value
                return
        raise ValueError("Phone not found")

    def add_birthday(self, date):
        self.birthday = BirthDate(date)

    def __str__(self):
        phones = ", ".join(p.value for p in self.phones)
        bday = f" | Birthday: {self.birthday.value}" if self.birthday else ""
        return f"{self.name.value}: {phones}{bday}"


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
            next_birthday = birth.replace(year=today.year)

            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)

            if next_birthday.weekday() == 5:
                next_birthday += timedelta(days=2)
            elif next_birthday.weekday() == 6:
                next_birthday += timedelta(days=1)

            days_left = (next_birthday - today).days

            if 0 <= days_left <= 7:
                result.append({
                    "name": record.name.value,
                    "birthday": next_birthday.strftime("%d.%m.%Y")
                })

        return result


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Error: {e}"
    return wrapper


@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)

    if not record:
        record = ContactRecord(name)
        book.add_record(record)

    record.add_phone(phone)
    return "Contact saved"


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)

    if not record:
        return "Contact not found"

    record.change_phone(old_phone, new_phone)
    return "Phone updated"


@input_error
def show_phone(args, book):
    record = book.find(args[0])
    if not record:
        return "Contact not found"
    return ", ".join(p.value for p in record.phones)


@input_error
def add_birthday(args, book):
    name, date = args
    record = book.find(name)
    if not record:
        return "Contact not found"
    record.add_birthday(date)
    return "Birthday added"


@input_error
def show_birthday(args, book):
    record = book.find(args[0])
    if not record or not record.birthday:
        return "Birthday not found"
    return record.birthday.value


@input_error
def birthdays(args, book):
    items = book.get_upcoming_birthdays()
    if not items:
        return "No birthdays this week"
    return "\n".join(f"{i['name']}: {i['birthday']}" for i in items)


def parse_input(text):
    return text.strip().split()


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input(">>> ")
        command, *args = parse_input(user_input)

        if command in ("exit", "close"):
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
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
            print("Invalid command.")


if __name__ == "__main__":
    main()
