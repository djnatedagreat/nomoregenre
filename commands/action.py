import inquirer

class Action:
    def require_arg(self, args, arg_name, prompt=None):
        if hasattr(args, arg_name):
            return getattr(args, arg_name)
        else:
            prompt_msg = prompt if prompt else arg_name + " is required. Please enter it now"
            prompt = [
                inquirer.Text("response", message=prompt_msg)
            ]
            answer = inquirer.prompt(prompt_msg)
            return answer["response"]
            