"""Stop only this completed Codex turn's obsolete Stop-hook continuation loop."""
import json
import os
from pathlib import Path
import socket
import time

HERE = Path(__file__).resolve().parent
THREAD = '01a167fa-f875-71b1-a5f4-f2ad741c8a7e'
TURN = '01a167fa-fb4e-7151-b085-e1636b5e5ac9'
SOCKET = '/home/jihoon/tmp/runtime/cxc-QlV92K/broker.sock'
assert os.environ.get('CODEX_THREAD_ID') == THREAD

receipt = dict(thread_id=THREAD, turn_id=TURN, action='turn/interrupt',
               reason='Optimization completed; intentionally removed Stop hook is cached in the running turn.',
               report=str(HERE/'REPORT.md'), status='prepared', timestamp=time.time())
def save():
    (HERE/'hook_interrupt_receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')

save()
try:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(10)
        client.connect(SOCKET)
        request = dict(id='L1-completed-turn-interrupt', method='turn/interrupt',
                       params=dict(threadId=THREAD, turnId=TURN))
        client.sendall((json.dumps(request)+'\n').encode())
        receipt['status']='sent'; save()
        stream=client.makefile('r')
        for line in stream:
            response=json.loads(line)
            if response.get('id') == request['id']:
                receipt['response']=response
                receipt['status']='acknowledged' if 'result' in response else 'rejected'
                save()
                break
        else:
            receipt['status']='connection_closed_before_acknowledgment';save()
except Exception as error:
    receipt['status']='error';receipt['error']=repr(error);save()
    raise
