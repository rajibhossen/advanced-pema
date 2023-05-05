from action_executor.action_manager import SshClient
from system_metrics.collector_backend import get_cpu_utilization
import threading


def apply_cpu_resource(pod_id, node, cpu):
    client = SshClient("ridl:ridl123@%s" % node)
    result = client.execute("python3 /home/ridl/rajibs_work/advanced_pema/action_executor/cpu_action.py %s %s " % (pod_id, round(cpu, 2)), sudo=True)
    # print(result)

#
# id = "/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-pod12c77f2e_160c_4ab0_b114_ea2cf7832404.slice/docker-730f5854b922aa258a578bb53a0e7018833b1310c82e26cc1d27cc6f798cee60.scope"
# node = "ridlserver07"
# cpu = 200000
# apply_cpu_resource(id, node, cpu)
