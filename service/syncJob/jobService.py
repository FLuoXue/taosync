"""
@Author：dr34m
@Date  ：2024/7/9 17:17 
"""
import logging
import re

from common.LNG import G
from mapper import jobMapper
from service.syncJob import jobClient

# 作业客户端列表，key为jobId,value为jobClient
jobClientList = {}


def initJob():
    """
    用于启动后寻找任务，修改异常终止状态，启动启用的任务
    :return:
    """
    logger = logging.getLogger()
    jobMapper.updateJobTaskStatusByStatus()
    jobList = jobMapper.getJobList()
    for item in jobList:
        try:
            logger.info(f"正在添加jobId为{item['id']}的任务")
            addJobClient(item, True)
        except Exception as e:
            logger.error(f"添加任务过程中报错")
            logger.exception(e)


def getJobClientById(jobId):
    """
    获取作业客户端
    :param jobId:
    :return:
    """
    jobId = int(jobId)
    global jobClientList
    if jobId in jobClientList:
        return jobClientList[jobId]
    job = jobMapper.getJobById(jobId)
    client = jobClient.JobClient(job)
    jobClientList[jobId] = client
    return client


def cleanJobInput(job):
    """
    清洗输入的数据
    :param job: job对象
    :return:
    """
    if job['isCron'] == 2 and job['enable'] != 1:
        job['enable'] = 1
    for key, value in job.items():
        if type(value) == str:
            if value.strip() == '':
                job[key] = None
            else:
                job[key] = value.strip()
    if job['exclude'] is not None:
        job['exclude'] = ":".join([item.strip() for item in job['exclude'].split(':')])
    if 'copyType' not in job or job['copyType'] is None:
        job['copyType'] = 0
    if 'dstAlistId' not in job or job['dstAlistId'] is None:
        job['dstAlistId'] = job['alistId']
    if int(job['copyType']) == 0 and int(job['dstAlistId']) != int(job['alistId']):
        raise Exception(G('copy_type_cross_engine_only_local'))
    if 'processEnable' not in job or job['processEnable'] is None:
        job['processEnable'] = 0
    if 'compareMode' not in job or job['compareMode'] is None:
        job['compareMode'] = 0
    try:
        job['compareMode'] = int(job['compareMode'])
    except Exception:
        job['compareMode'] = 0
    if job['compareMode'] not in [0, 1]:
        job['compareMode'] = 0
    if 'processTypes' not in job:
        job['processTypes'] = None
    if 'processFind' not in job:
        job['processFind'] = None
    if 'processReplace' not in job:
        job['processReplace'] = None
    if job.get('processTypes', None) is not None:
        cleanTypes = []
        for item in job['processTypes'].split(':'):
            cItem = item.strip().lower()
            if not cItem:
                continue
            if not cItem.startswith('.'):
                cItem = '.' + cItem
            cleanTypes.append(cItem)
        job['processTypes'] = ":".join(cleanTypes)
        if job['processTypes'] == '':
            job['processTypes'] = None
    if int(job['processEnable']) == 1:
        if int(job['copyType']) != 1:
            raise Exception(G('process_only_local_copy'))
        if job.get('processTypes', None) is None:
            raise Exception(G('process_types_required'))
        if job.get('processFind', None) is None:
            raise Exception(G('process_find_required'))
        if job.get('processReplace', None) is None:
            job['processReplace'] = ''
        try:
            re.compile(job['processFind'])
        except Exception:
            raise Exception(G('process_find_invalid'))
    else:
        job['processTypes'] = None
        job['processFind'] = None
        job['processReplace'] = None


def addJobClient(job, isInit=False):
    """
    新增作业客户端
    :param isInit: 是否是初始化过程
    :param job: {
        enable: 1,
        srcPath: '',
        dstPath: '',
        alistId: null,
        speed: 0,
        method: 0,
        interval: 60
    }
    :return:
    """
    cleanJobInput(job)
    client = jobClient.JobClient(job, isInit)
    global jobClientList
    jobClientList[int(client.jobId)] = client


def editJobClient(job):
    """
    编辑作业客户端
    :param job: {
        id: 1,
        enable: 1,
        srcPath: '',
        dstPath: '',
        alistId: null,
        speed: 0,
        method: 0,
        interval: 60
    }
    """
    jobId = int(job['id'])
    cleanJobInput(job)
    client = getJobClientById(jobId)
    if client.job['enable'] == 1 and client.job['isCron'] != 2:
        raise Exception(G('disable_then_edit'))
    client.stopJob(remove=True)
    global jobClientList
    del jobClientList[jobId]
    client = jobClient.JobClient(job)
    jobMapper.updateJob(job)
    jobClientList[jobId] = client


def doAllJobManual():
    """
    手动执行所有未禁用的作业
    :return:
    """
    jobList = jobMapper.getEnableJobList()
    if not jobList:
        raise Exception(G('no_job_for_run'))
    for jobItem in jobList:
        client = getJobClientById(jobItem['id'])
        if client.job['enable'] == 1:
            client.doManual()


def doJobManual(jobId):
    """
    手动执行作业
    :param jobId:
    :return:
    """
    client = getJobClientById(jobId)
    if client.job['enable'] != 1:
        raise Exception(G('disabled_job_cannot_run'))
    client.doManual()


def removeJobClient(jobId):
    """
    删除作业
    :param jobId:
    :return:
    """
    jobId = int(jobId)
    client = getJobClientById(jobId)
    client.stopJob(remove=True)
    jobMapper.deleteJob(jobId)
    global jobClientList
    del jobClientList[jobId]


def continueJob(jobId):
    """
    启用作业
    :param jobId:
    """
    client = getJobClientById(jobId)
    client.resumeJob()


def pauseJob(jobId):
    """
    禁用作业
    :param jobId:
    """
    client = getJobClientById(jobId)
    if client.job['isCron'] == 2:
        raise Exception(G('cannot_disable_manual_job'))
    client.stopJob()


def abortJob(jobId):
    """
    中止作业
    :param jobId:
    :return:
    """
    client = getJobClientById(jobId)
    client.abortJob()


def getJobList(req):
    """
    作业列表
    :param req: {
        'pageSize': 1,
        'pageNum': 2
    }
    :return:
    """
    return jobMapper.getJobList(req)


def getJobCurrent(jobId, status=None):
    """
    获取当前作业正在执行中的任务的详情
    :param jobId:
    :param status: 状态
    :return:
    """
    client = getJobClientById(int(jobId))
    taskClient = client.currentJobTask
    if taskClient is not None:
        if status is None:
            return taskClient.getCurrent()
        else:
            return taskClient.getCurrentByStatus(int(status))
    return None
