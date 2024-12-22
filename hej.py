from cryptography.fernet import Fernet

# Skapa en ny nyckel och skriv ut den för att använda den senare
new_key = Fernet.generate_key()
print(new_key.decode())  # Detta är din nya nyckel
