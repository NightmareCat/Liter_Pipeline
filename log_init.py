import logging
import sys

# 定义一个自定义格式化器，用于给不同级别的日志添加颜色
class ColorFormatter(logging.Formatter):
    # ANSI 转义码：终端控制颜色
    COLOR_MAP = {
        'DEBUG': "\033[37m",     # 灰色
        'INFO': "\033[36m",      # 青色
        'WARNING': "\033[33m",   # 黄色
        'ERROR': "\033[31m",     # 红色
        'CRITICAL': "\033[41m",  # 红底白字
    }
    RESET = "\033[0m"  # 重置颜色为默认

    # 重写 format 方法，实现彩色日志级别输出
    def format(self, record):
        # 取当前日志级别的颜色码，若找不到则默认不加颜色
        color = self.COLOR_MAP.get(record.levelname, self.RESET)

        # 给 levelname 和 message 加上颜色（只影响输出文本，不影响日志逻辑）
        record.levelname = f"{color}{record.levelname:<8}{self.RESET}"  # 保证日志级别对齐
        record.msg = f"{color}{record.msg}{self.RESET}"

        # 调用父类格式化方法（使用我们定义的格式）
        return super().format(record)

# 封装一个函数用于快速创建 logger 实例
def setup_logger(name: str) -> logging.Logger:
    """
    根据模块名 name 创建并返回一个已配置的 logger 实例
    """
    # 创建一个格式化器，定义日志输出格式和时间格式
    formatter = ColorFormatter(
        fmt="%(asctime)s | %(levelname)s | %(module)s.%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 创建一个输出到控制台的 handler（也可以换成 FileHandler 输出到文件）
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)  # 绑定彩色格式器

    # 创建或获取一个 logger 实例，名字通常为模块名（__name__）
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # 设置最低输出级别为 DEBUG（全部显示）

    # 防止重复添加 handler（如果 logger 已存在 handler）
    if not logger.handlers:
        logger.addHandler(handler)
        logger.propagate = False  # 禁止向父 logger 传播，防止重复打印

    return logger
