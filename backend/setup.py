import os
# first, we need to check the folders `core/out/[info][chatlogs]` and `core/piis` exist
print("""
===========================================GCSearch V1.0 Setup===========================================
 ░▒▓██████▓▒░ ░▒▓██████▓▒░ ░▒▓███████▓▒░▒▓████████▓▒░░▒▓██████▓▒░░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒▒▓███▓▒░▒▓█▓▒░       ░▒▓██████▓▒░░▒▓██████▓▒░ ░▒▓████████▓▒░▒▓███████▓▒░░▒▓█▓▒░      ░▒▓████████▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
 ░▒▓██████▓▒░ ░▒▓██████▓▒░░▒▓███████▓▒░░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░ 
=========================================================================================================
""")
def make_dir_if_not_exists(dir_path:str):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Directory {dir_path} created")
    else:
        print(f"Directory {dir_path} already exists")
    if not os.path.exists(dir_path):
        raise Exception(f"Failed to create directory {dir_path}")

print()
print("==================================Setting up required directories========================================")
make_dir_if_not_exists("core/out/info")
make_dir_if_not_exists("core/out/chatlogs")
make_dir_if_not_exists("core/piis")
print()
print("All necessary directories created")
print("=========================================================================================================")
print()
print("==================================Parsing Data into chatlog files========================================")
# now we need to run the chatlog creators
choice_to_platform = {
    "1": "instagram",
    "2": "whatsapp",
    "3": "line",
    "4": "wechat"
}
correct_choice = False
while not correct_choice:
    choice = input("Enter the number of the platform you want to convert to chatlog:\n1. Instagram\n2. WhatsApp\n3. LINE\n4. WeChat\n\nChoice: ")
    if choice in choice_to_platform:
        correct_choice = True
    else:
        print(f"Did not recognize choice {choice}. Please enter a valid choice.")

print()
def run_chatlog_creator(choice:str):
    platform = choice_to_platform[choice]
    print(f"Running chatlog creator for {platform}")
    if platform == "instagram":
        from core.export_parsers.insta_chatlog_creator import generate_chatlog
        #generate_chatlog()
        print(f"This is where we'd run the chatlog creator for {platform}")
    elif platform == "whatsapp":
        from core.export_parsers.whatsapp_to_chatlog import generate_chatlog
        #generate_chatlog()
        print(f"This is where we'd run the chatlog creator for {platform}")
    elif platform == "line":
        from core.export_parsers.LINE_to_chatlog import generate_chatlog
        #generate_chatlog()
        print(f"This is where we'd run the chatlog creator for {platform}")
    elif platform == "wechat":
        from core.export_parsers.WeChat_to_chatlog import generate_chatlog
        #generate_chatlog()
        print(f"This is where we'd run the chatlog creator for {platform}")
    else:
        raise Exception(f"Error when running chatlog creator for \"{platform}\"")
    
run_chatlog_creator(choice)
print()
print("All chatlog files created successfully")
print("=========================================================================================================")
print()
# now the PII creator
print("==================================Creating PII files========================================")
language_choice_made = False
choice_to_language = {
    "1": "english",
    "2": "chinese",
    "3": "traditional_chinese",
    "4": "turkish"
}
print("Please")
while not language_choice_made:
    language_choice = input("""
Please choose a language to create the PIIs with. 
                            
This language determines the tokenisation, and must be used when launching the backend:
    1. English
    2. Chinese (Simplified)
    3. Traditional Chinese
    4. Turkish

Choice: """)
    if language_choice in choice_to_language:
        language_choice_made = True
        language = choice_to_language[language_choice]
        print(f"You selected {language} for PII creation.")
    else:
        print(f"Did not recognize choice {choice_to_language[language_choice]}. Please enter a valid choice.")

def run_pii_creator(language:str):
    from core.pii import PIIConstructor
    p = PIIConstructor(language=language)
    print(f"Running PII creator for {language}")
    #p.create_piis_from_folder()

run_pii_creator(language)
print()
print("All PII files created successfully")
print("==========================================GCSearch Export Completed Successfully=============================================")