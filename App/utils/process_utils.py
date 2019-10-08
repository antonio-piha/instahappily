import os
import base64
import psutil
import sys
import subprocess
from multiprocessing import Process, Manager
from time import sleep
from ..settings import Environment
from ..logger import Logger

log = Logger.get(__name__)

# Worker's job:
# Process
#   Subrocess
#
# Process: self._process starts Worker._target
#    Subprocess: Worker._target starts subprocess
#    - subprocess.join which will make parent process wait

# Using shared memory
class Worker:
  def __init__(self, target_func=None):
    # We must set_metadata separately, not through the constructor
    # to avoid executing with wrong meta_data
    self.meta_data = None
    self.target_func = target_func
    self._manager = Manager()
    self._state = self._manager.dict()
    self._state['unique_id'] = base64.b64encode(os.urandom(5)).decode('UTF-8')
    self._state['run_forever'] = False
    self._process = None
  def run_forever(self, run_forever = None):
    if run_forever:
      self._state['run_forever'] = True
  def running(self):
    if not self._process:
      return False
    return self._process.is_alive()
  def cancel(self):
    if not self._process:
      return
    try:
      properly_terminate_process(pid=self._process.pid)
    except Exception as exc:
      log.warning(exc, exc_info=True)
  def start(self):
    self.cancel()
    self._process = Process(target=Worker._target, args=(self.meta_data, self._state, self.target_func,))
    # start must be called not more than once per process object
    self._process.start()
  @staticmethod
  def _target(meta_data, state, _target_func):
    #####################################################
    # This proc will be run in first level subprocess !!!
    #####################################################
    unique_id = state['unique_id']
    log.info("[{}] First level subprocess started.".format(unique_id))
    if not _target_func:
      return
    while True:
      subprocess = None
      try:
        subprocess = Process(target=_target_func, args=(meta_data,))
        subprocess.start()
        # important sleep to make sure that subprocess gets cpu cycle and pid
        sleep(0.1)
        log.info("[{}] Second level subprocess started.".format(unique_id))
        subprocess.join()
        log.info("[{}] Second level subprocess finished.".format(unique_id))
      except Exception as exc:
        log.warning(exc,exc_info=True)
      finally:
        # Clean up
        # We need to do this in case or repeated failures inside the _target_func
        # Otherwise because we're insde while loop, we could create unexpectedly great number of processes and orphans
        if subprocess is not None:
          properly_terminate_process(pid=subprocess.pid)
      # This is to cover eventual uncaught exceptions inside the subprocess (session run)
      # Another similar check is inside the session run itself
      if state['run_forever'] == False:
        break
    log.info("[{}] First level subprocess finished.".format(unique_id))

class Executor:
  def __init__(self):
    try:
      self.workers = {}
      self.log = log
    except Exception as exc:
      log.error(exc, exc_info=True)
  def is_worker_running(self, worker_id):
    if worker_id not in self.workers:
      return False
    return self.workers[worker_id].running()
  def worker_start(self, worker_id, meta_data, target_func, run_forever = None):
    try:
      if worker_id in self.workers:
        worker = self.workers[worker_id]
        worker.cancel()
      else:
        worker = Worker(target_func=target_func)
        self.workers[worker_id] = worker
      # We must explicitly set metadata to refresh metadata in worker existing instance
      worker.meta_data = meta_data
      worker.run_forever(run_forever)
      worker.start()
    except Exception as exc:
      log.error(exc, exc_info=True)
      return False
    return True
  def worker_stop(self, worker_id):
    if worker_id not in self.workers:
      return True
    worker = self.workers[worker_id]
    if self.is_worker_running(worker_id):
      worker.cancel()
    return True
  def cleanup(self):
    for worker in self.workers:
      try:
        worker.cancel()
      except Exception as exc:
        log.warning(exc, exc_info=True)

def properly_terminate_process(pid):
  if not psutil.pid_exists(pid):
    return
  parent = psutil.Process(pid)
  if not parent:
    return
  if Environment.is_windows:
    properly_terminate_process_on_windows(pid)
  else:
    children = parent.children(recursive=True)
    for child in children:
      child.terminate()
    gone, still_alive = psutil.wait_procs(children, timeout=5)
    for p in still_alive:
      p.kill()
  parent.kill()
  parent.wait(5)

def properly_terminate_process_on_windows(pid):
    dev_null = open(os.devnull, 'w')
    command = ['TASKKILL', '/F', '/T', '/PID', str(pid)]
    proc = subprocess.Popen(command, stdin=dev_null, stdout=sys.stdout, stderr=sys.stderr)

