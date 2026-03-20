import inquirer
from models import Creator

class Action:
    def require_arg(self, args, arg_name, prompt=None):
        if getattr(args, arg_name, None) is not None:
            return getattr(args, arg_name)
        else:
            prompt_msg = prompt if prompt else str(arg_name) + " is required. Please enter it now"
            prompt = [
                inquirer.Text("response", message=prompt_msg)
            ]
            answer = inquirer.prompt(prompt)
            return answer["response"]
            
    def require_creator(self, args, arg_name, prompt=None):
        creator_options = []
        for c in Creator.select():
            creator_options.append((c.name, c.id))
        #creator_name = None
        if getattr(args, arg_name, None) is not None:
            creator_name = getattr(args, arg_name)
            return Creator.get_or_none(Creator.name == creator_name)
        else:
            prompt_msg = prompt if prompt else str(arg_name) + " is required. Please choose a creator."
            creator_prompt = [
                inquirer.List("creator", message=prompt_msg, choices=creator_options)
            ]
            answer = inquirer.prompt(creator_prompt)
            return Creator.get_by_id(answer["creator"])