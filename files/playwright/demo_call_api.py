

class Api:
    """
    API调用处理类，用于封装多个API方法的执行逻辑，支持数据交换。

    该类设计用于集中管理API方法的调用过程，包括参数传递、方法执行、结果收集等。
    主要用于需要批量处理多个方法调用的场景，例如API网关、任务调度等。
    提供了数据交换功能，允许在方法调用之间传递和更新数据。

    Attributes:
        swap: 用于存储方法执行后的数据，以便在不同调用之间进行数据交换。
        params (dict): 由构造函数传入的参数字典，用于存储方法调用配置或其他自定义参数。

    Methods:
        call(Class, List): 执行列表中的API方法调用，支持实例方法和独立函数。
        demo(x): 示例方法，用于演示API方法调用。

    Example:
        >>> api = Api(**{"demo": {"params": {"x": 2}}})
        >>> result = api.call(Class=api, List=[{"demo": {"params": {"x": 2}}}])
        >>> print(result)
        {'Api': [{'demo': {'utc': 1633072800.123456, 'params': {'x': 2}, 'exec': True, 'res': 4}}]}

    Note:
        1. call方法中的Class参数应传递实例而非类本身
        2. List参数中的字典结构需要严格按照{"方法名": {"params": 参数字典}}格式
        3. demo方法仅作演示用途，实际使用中需替换为具体业务逻辑
        4. call方法可以处理实例方法和独立函数调用
        5. self.swap用于存储方法执行后的数据，以便在不同调用之间进行数据交换
    """

    def __init__(self, **kwargs):
        """
        初始化Api实例。

        Args:
            **kwargs: 用于初始化params属性的字典，可以包含任意键值对。
                      例如，可以传递方法调用配置，这些配置将存储在params属性中。
                      在调用call方法时，这些配置可以用于指定要调用的方法及其参数。

        初始化过程中，将传入的关键字参数存储在params属性中，并初始化swap属性为None。
        swap属性用于存储方法执行后的数据，以便在不同调用之间进行数据交换。
        """

        self.swap = None
        self.params = kwargs

    def call(Class=None, List=list()):
        """
        执行列表中的API方法调用，支持实例方法和独立函数调用，以及数据交换。

        该方法遍历传入的列表，对每个字典项中的方法进行动态调用，
        收集执行结果并附加时间戳信息。支持处理实例方法和独立函数调用。
        方法执行结果可以通过self.swap在不同调用之间进行数据交换。

        Args:
            Class: 包含目标方法的类实例或函数。可以是任意具有可调用方法的对象。
            List (list): 方法调用配置列表，每个元素为字典。每个字典应包含方法名和对应的参数。
                         例如，[{"方法名": {"params": 参数字典}}]。

        Returns:
            dict: 以类名为键，值为执行结果列表的字典。每个执行结果包含时间戳、参数、执行状态和结果。
                  例如，{"类名": [{"方法名": {"utc": 时间戳, "params": 参数, "exec": 执行状态, "res": 结果}}]}。

        Raises:
            BaseException: 捕获方法执行过程中的异常。

        逻辑流程：
            1. 遍历传入的方法调用列表。
            2. 对于每个方法调用配置项：
                a. 动态获取Class对象中对应的方法。
                b. 检查方法是否可调用且配置项包含参数。
                c. 执行方法并捕获异常。
                d. 将方法执行结果存储到self.swap中，以便在不同调用之间进行数据交换。
                e. 记录方法执行的时间戳、参数、执行状态和结果。
            3. 返回包含所有方法执行结果的字典。

        数据交换机制：
            - self.swap用于存储每个方法执行后的返回值。
            - 在后续的方法调用中，可以通过访问self.swap来获取之前方法的执行结果。
            - 这允许方法之间共享数据，实现数据交换和流程控制。
        """

        from time import time
        swap_call = None
        for Dict in List:
            for f1 in Dict:
                swap_exec = getattr(Class, f1, None)
                try:
                    if (callable(swap_exec) and "params" in Dict[f1]):
                        swap_call = swap_exec(**Dict[f1]["params"].copy())
                        swap_exec = callable(swap_exec)
                except BaseException as e:
                    swap_exec = False
                Dict[f1] = {
                    "utc": time(),
                    "params": Dict[f1]["params"],
                    "exec": swap_exec,
                    "res": swap_call
                }
                swap_call = None
        return {Class.__name__ if isinstance(Class, type) else Class.__class__.__name__: List}

    def demo(self, x):
        """
        示例方法，用于演示API方法调用。

        Args:
            x (int): 输入参数。

        Returns:
            int: 输入参数的两倍值。

        该方法接收一个整数参数x，返回x的两倍值。
        用于演示如何定义可被call方法调用的API方法。
        """

        return x * 2


def demo():
    """
    示例函数，展示Api类的基本使用方法。

    Returns:
        dict: Api方法调用结果。

    该函数创建一个Api实例，配置并执行一个方法调用，然后返回执行结果。
    用于演示如何使用Api类进行方法调用和数据交换。
    """
    
    api = [
        {
            "demo": {
                "params": {"x": __file__}
            }
        }
    ]
    api = Api(**api[0]).call(api)
    return api


if __name__ == '__main__':
    print(demo())
