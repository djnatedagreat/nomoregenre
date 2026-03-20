import argparse
from models import Show
from tabulate import tabulate

class ListShowAction:

    def run(self):
        shows = Show.select()
        headers = ['ID', 'Name', 'First Air Date', 'Build Date']
        data = []
        for s in shows:
            data.append([s.id, s.name, s.first_air_date.strftime("%Y-%m-%d"), s.build_date.strftime("%Y-%m-%d") if s.build_date else ''])
            #print ("(" +Fore.WHITE+Style.BRIGHT+ str(s.id) + Style.RESET_ALL+ ")\t" + s.first_air_date.strftime("%Y-%m-%d"))
        print(tabulate(data, headers=headers, tablefmt="pipe"))
            #print ("("+str(a.id)+") "+a.type.name + "\t" + a.creator.name + "\t" + a.name)

# kwargs "at" for asset_type filter eg. mix, id, etc. assumes asset type name 
def handle(args, **kwargs):
    parser = argparse.ArgumentParser(description="List Shows")
    parsed_args = parser.parse_args(args)
    action = ListShowAction()
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)