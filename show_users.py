from user_seed_data import INDIAN_USERS

print('📧 Available users for login:')
print('=' * 50)

for i, user in enumerate(INDIAN_USERS, 1):
    print(f'{i}. {user["personal_info"]["first_name"]} {user["personal_info"]["last_name"]}')
    print(f'   Email: {user["email"]}')
    print(f'   Password: {user["password"]}')
    print(f'   Role: {user["professional_info"]["current_role"]}')
    print(f'   Company: {user["professional_info"]["current_company"]}')
    print()
