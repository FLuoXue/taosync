import configparser
import logging
import os

from common.commonUtils import generatePasswd, readOrSet

sysConfig = None


def getPasswordStr():
    """
    获取加密字符串
    :return: 加密字符串
    """
    fileName = 'data/secret.key'
    passwdStr = readOrSet(fileName, generatePasswd(256))
    return passwdStr


def getConfig():
    global sysConfig
    if sysConfig is None:
        passwdStr = getPasswordStr()
        dbname = 'data/taoSync.db'
        sCfg = {
            'port': 8023,
            'expires': 2,
            'log_level': 1,
            'console_level': 2,
            'log_save': 7,
            'task_save': 0,
            'timeout': 72,
            'copy_cache_max_mb': 1024
        }
        if os.path.exists('data/config.ini'):
            try:
                cfg = configparser.ConfigParser()
                cfg.read('data/config.ini', encoding='utf8')
                tao = cfg['tao']
                for keyItem in sCfg.keys():
                    if keyItem in tao:
                        sCfg[keyItem] = int(tao[keyItem])
            except Exception as e:
                logger = logging.getLogger()
                logger.error(f"配置文件读取失败，将使用默认配置_/_config.ini read error: {e}")
                logger.exception(e)
        else:
            try:
                sCfg['port'] = int(os.getenv('TAO_PORT', 8023))
                sCfg['expires'] = int(os.getenv('TAO_EXPIRES', 2))
                sCfg['log_level'] = int(os.getenv('TAO_LOG_LEVEL', 1))
                sCfg['console_level'] = int(os.getenv('TAO_CONSOLE_LEVEL', 2))
                sCfg['log_save'] = int(os.getenv('TAO_LOG_SAVE', 7))
                sCfg['task_save'] = int(os.getenv('TAO_TASK_SAVE', 0))
                sCfg['timeout'] = int(os.getenv('TAO_TASK_TIMEOUT', 72))
                sCfg['copy_cache_max_mb'] = int(os.getenv('TAO_COPY_CACHE_MAX_MB', 1024))
            except Exception as e:
                logger = logging.getLogger()
                logger.error(f"环境变量读取失败，将使用默认配置_/_ENV read error: {e}")
                logger.exception(e)
        sysConfig = {
            'db': {
                'dbname': dbname
            },
            'server': {
                'passwdStr': passwdStr,
                **sCfg
            }
        }
    return sysConfig


def updateServerConfig(configMap):
    """
    更新并持久化后端配置
    :param configMap: 仅支持server下的数字配置
    :return:
    """
    if not configMap:
        return
    cfg = getConfig()
    if 'server' not in cfg:
        cfg['server'] = {}
    for keyItem, keyVal in configMap.items():
        cfg['server'][keyItem] = int(keyVal)

    cfgFile = configparser.ConfigParser()
    if os.path.exists('data/config.ini'):
        cfgFile.read('data/config.ini', encoding='utf8')
    if 'tao' not in cfgFile:
        cfgFile['tao'] = {}
    for keyItem, keyVal in configMap.items():
        cfgFile['tao'][keyItem] = str(int(keyVal))
    with open('data/config.ini', 'w', encoding='utf8') as fp:
        cfgFile.write(fp)
