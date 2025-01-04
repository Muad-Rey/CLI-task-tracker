try:
    import beautifull_terminal
except ModuleNotFoundError:
    ...
finally:
    import json
    from datetime import datetime
    from sys import argv

# all the code is base on this "OPERATIONS" constant DO NOT CHANGE the order of items in it otherwise everything would break
OPERATIONS = ['add', 'mark-in-progress', 'mark-done', 'update', 'delete', 'list']

class Task:
    @classmethod
    @property
    def __filename(self):
        name = 'data'
        return f'{name}.json'
    def __init__(self, name: str, id: int | None = None):
        self.id = id if id else self.__get_id
        self.__delete = False
        self.__stats = ['todo', 'in-progress', 'done']
        self.name = name
        self.status = 'todo'
        self.createdAt = datetime.today().ctime()
        self.updatedAt = None

    @classmethod
    def load(cls, status: str | None = None):
        instances = []
        try:
            with open(str(cls.__filename)) as file:
                tasks : list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return instances
        for tsk in tasks:
            self = cls(tsk['name'], tsk['id'])
            self.status = tsk['status']
            self.createdAt = tsk['createdAt']
            self.updatedAt = tsk['updatedAt']
            instances.append(self)
        if status:
            new_list = []
            status = status.lower().strip()
            for i, instance in enumerate(instances):
                if instance.status == status:
                    new_list.append(instance)
            return new_list
        return instances
    @classmethod
    def get(cls, id: int):
        if tasks := cls.load():
            for tsk in tasks:
                if tsk.id == id:
                    return tsk
        return None


    def delete(self):
        self.__delete = True
        if self.save():
            return self.name
        else:
            raise Exception('unknown error task was not deleted')
    def update(self, name):
        self.name = name
        self.updatedAt = datetime.today().ctime()
        if self.save():
            return self.name
        else:
            raise Exception('unknown error task was not saved')

    def setstatus(self, state:str):
        if state in self.__stats:
            self.status = state
            self.updatedAt = datetime.today().ctime()
            if self.save():
                return self.status
            else:
                raise Exception('unknown error task was not saved')
        else:
            raise Exception(f"unsupported state {state}")

    def __str__(self):
        return (f'Name: "{self.name}", ID: {self.id}, Status: {self.status}, '
                f'Created: {self.createdAt}, Updated: {self.updatedAt}')

    @property
    def json(self):
        try:
            self.__dict__.pop('_Task__stats')
            self.__dict__.pop('_Task__delete')
            self.__dict__.pop('_Task__filename')
        except KeyError:
            ...
        finally:
            return self.__dict__

    def save(self):
        file_list = []
        try:
            with open(self.__filename) as data_file:
                file_list: list = json.load(data_file)

                if self.__delete:
                    file_list.pop(file_list.index(self.json))
                    with open(self.__filename, 'w') as file:
                        json.dump(file_list, file, indent=2)
                        return True

                for i, item in enumerate(file_list):
                    if self.id == item['id']:
                        file_list[i] = self.json
                        with open(self.__filename, 'w') as file:
                            json.dump(file_list, file, indent=2)
                            return True

        except (FileNotFoundError, json.JSONDecodeError):
            ...

        file_list.append(self.json)
        with open(self.__filename, 'w') as file:
            json.dump(file_list, file, indent=2)
            return True

    @property
    def __get_id(self):
        try:
            with open(self.__filename) as file:
                try:
                    file_list :list = json.load(file)
                    return file_list[-1]['id'] + 1
                except json.JSONDecodeError:
                    return 1
        except FileNotFoundError:
            return 1

def main():
    check_arguments()
    arg_len = len(argv)
    operation = argv[1].lower().strip()
    if operation == OPERATIONS[5]:
        list_()
    elif arg_len == 3 and operation in OPERATIONS:
        if operation == OPERATIONS[0]:
            add()
        elif operation == OPERATIONS[4]:
            delete()
        elif operation == OPERATIONS[1] or operation == OPERATIONS[2] and argv[2].isnumeric():
            update_progress(operation)
    elif operation in OPERATIONS and arg_len == 4 and operation == OPERATIONS[3] and argv[2].isnumeric():
        update()

def usage(operation: str = None) -> str:
    base = f'usage ./{argv[0]} '
    if not operation:
        ops = str(OPERATIONS).strip('[').strip(']').replace("'", '')
        return base + f'(Operation: {ops}) (name or id)'
    elif operation == OPERATIONS[0]:
        return base + f'{operation} "Task Name or Description"'
    elif operation == OPERATIONS[5]:
        return base + f'{operation} + (done, in-progress, todo) if you want to list by state'
    else:
        return base + f'{operation} (Task ID)'
# ['add', 'mark-in-progress', 'mark-done', 'update', 'delete', 'list']


def pprint(*args, **kwargs) -> None:
    try:
        color = kwargs.pop('color')
        # noinspection PyArgumentList
        print(*args, color=color, **kwargs)
    except (KeyError, TypeError):
        print(*args, **kwargs)


def check_arguments():
    if len(argv) == 1:
        pprint(usage(), color='orange')
        exit(1)

    elif len(argv) == 2:
        op = argv[1].lower().strip()
        if op  == OPERATIONS[5]:
            return
        elif op in OPERATIONS and OPERATIONS[0] == op:
            pprint(usage(op), color='cyan')
            # pprint('operation found', argv[1], color='green')
            exit(1)
        elif op in OPERATIONS and op == OPERATIONS[1] or op == OPERATIONS[2]:
            pprint(usage(op), color='orange')
        elif op not in OPERATIONS:
            pprint('invalid operation', argv[1], color='orange')
            ops = str(OPERATIONS).strip('[').strip(']').replace("'", '')
            pprint(f'supported arguments: {ops}', color='cyan', end='.\n')
            exit(1)
        else:
            pprint(usage(op), color='orange')
def add():
    task = Task(argv[2])
    task.save()
    pprint(f'Task was added successfully (ID: {task.id})', color='green')


def delete():
    if task := Task.get(int(argv[2])):
        pprint('Task found: ', color='blue', end=' ')
        pprint(task, color='magenta')
        pprint("Are you sure you want to delete this task? yes or y to delete", color='orange', end=' ')
        ans = input().strip().lower()
        if ans == 'y' or ans == 'yes':
            task.delete()
            pprint('The Task was deleted successfully', color='yellow')
        else:
            pprint('operation canceled', color='cyan')
    else:
        pprint('No task was found with the provided ID:', argv[2], color='yellow')
def update_progress(operation):
    operation = operation.lstrip('mark-')
    if task := Task.get(int(argv[2])):
        task.setstatus(operation)
        pprint(f'Task was successfully marked {operation} (ID: {task.id})', color='blue')
    else:
        pprint('No task was found with the provided ID:', argv[2], color='yellow')

def update():
    if task := Task.get(int(argv[2])):
        task.update(argv[3])
        pprint(f'Task was updated successfully (ID: {task.id})', color='blue')
    else:
        pprint('No task was found with the provided ID:', argv[2], color='yellow')

def list_():
    if len(argv) == 3:
        ar = argv[2].strip().lower()
        if ar == 'done' or ar == 'in-progress' or ar == 'todo':
            tasks = Task.load(argv[2])
        else:
            pprint(usage('list'), color='orange')
            exit(1)
    else:
        tasks = Task.load()
    if len(tasks) == 0:
        pprint('No matching tasks', color='yellow')
    for task in tasks:
        print()
        pprint(task, color='cyan')


if __name__ == '__main__':
    main()