import os
import dotenv
dotenv.load_dotenv()

  
def add_env_variable(env_path:str, key: str, value:str):
    """
    Add a new key-value pair to a .env file.
    
    Args:
        key (str): The key of the variable.
        value (str): The value of the variable.
        path (str): Path to the .env file.
    """
    if os.path.exists(env_path):
        # Read the existing content of the .env file
        with open(env_path, 'r') as env_file:
            lines = env_file.readlines()

        env_variable = f'{key} = {value}\n'
        # Check if the variable already exists
        variable_exists = False
        
    # Check if the variable already exists and replace it
        for i, line in enumerate(lines):
            # Use strip to remove any leading/trailing whitespace including newlines
           # print(f"Checking line {i}: {line.strip()}")
            if line.strip().startswith(f"{key}"):
                lines[i] = env_variable
                variable_exists = True
                #print(f"Updated {key} in .env file.")
                break
        # If the variable doesn't exist, append it to the bottom
        if not variable_exists:
            lines.append(f"{env_variable}\n")
           # print(lines)

            # Write the modified content back to the .env file
            with open(env_path, 'w') as env_file:
                env_file.writelines(lines)

        return env_variable
    else:
        print("Error:Env Path not found ")
        return None


#env_path = '../.env'

#add_env_variable(env_path, 'TEST', '"hiu"')

#add_env_variable(env_path, 'TEST', '"haaaaaaaaaau"')