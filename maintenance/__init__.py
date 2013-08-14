"""
Install me as a cron job to run every minute:

* * * * * yang     bash .../scrub.bash
"""

import sys, os, subprocess as subp, pync, psutil, time, pipes

def is_on_battery():
  if sys.platform == 'darwin':
    return 'AC Power' not in subp.check_output('pmset -g batt'.split())
  else:
    return False

def suspend_running_bitrot():
  p = get_running_bitrot()
  if p:
    print 'Suspending %s' % p.pid
    p.suspend()

def get_running_bitrot():
  for p in psutil.process_iter():
    try: cmdline = p.cmdline
    except: pass
    else:
      if len(cmdline) >= 2 and 'python' in cmdline[0] and 'bitrot' in cmdline[1]:
        return p
  return None

def main(argv=sys.argv):
  suspendcmd = ' '.join(['bash',
    pipes.quote(os.path.join(os.path.dirname(__file__), 'scrub.bash')),
    'suspend'])

  # if on battery or explicitly suspending
  if is_on_battery():
    print 'On battery'
    suspend_running_bitrot()
    return

  if len(argv) > 1:
    print 'Suspending per explicit request (>0 args)'
    suspend_running_bitrot()
    return

  running_bitrot = get_running_bitrot()
  if running_bitrot:
    pync.Notifier.notify('Resuming bitrot scubber. Click to suspend for 4h.',
        execute=suspendcmd)
    running_bitrot.resume() # in case it was suspended
    return

  # if scrub ran too recently (run according to schedule, e.g. every 1h):
  timestamp_path = os.expanduser('~/.maintenance-timestamp')
  with open(timestamp_path) as f: last_start_time = int(f.read())
  if time.time() - last_start_time < 30 * 24 * 60 * 60:
    print 'Last start was less than a month ago (%s)' % \
        dt.datetime.fromtimestamp(last_start_time)
    return

  # run scrub
  pync.Notifier.notify('Started bitrot scrubber. Click to suspend for 4h.',
      execute=suspendcmd)
  p = psutil.Process(os.getpid())
  p.set_nice(20)
  p.set_ionice(psutil.IOPRIO_CLASS_IDLE, 7)
  with open(timestamp_path, 'w') as f: f.write(time.time())
  execl('bitrot')

# vim: et sw=2 ts=2
