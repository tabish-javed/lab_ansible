#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import os
import pwd
import platform


def user_exists(username):
  try:
    return pwd.getpwnam(username)
  except KeyError:
    return None


def is_home_dir_missing(path):
  return not os.path.exists(path)


def run_module():
  module_args = dict(
      users=dict(type='list', required=True, elements='str')
  )

  result = dict(
      changed=False,
      created_dirs=[],
      skipped_users=[]
  )

  module = AnsibleModule(
      argument_spec=module_args,
      supports_check_mode=True
  )

  users = module.params['users']

  for username in users:
    user_info = user_exists(username)
    if not user_info:
      result['skipped_users'].append(f"{username} (not found)")
      continue

    home_dir = user_info.pw_dir

    if not is_home_dir_missing(home_dir):
      result['skipped_users'].append(f"{username} (home exists)")
      continue

    # Optional Solaris autofs check — skip if parent is a mount point like /home
    if os.path.ismount(os.path.dirname(home_dir)):
      result['skipped_users'].append(f"{username} (autofs mount)")
      continue

    if module.check_mode:
      result['created_dirs'].append(home_dir)
      continue

    try:
      os.makedirs(home_dir, mode=0o755)
      os.chown(home_dir, user_info.pw_uid, user_info.pw_gid)
      result['created_dirs'].append(home_dir)
      result['changed'] = True
    except Exception as e:
      module.fail_json(msg=f"Error creating home for {username}: {str(e)}", **result)

  module.exit_json(**result)


def main():
  if platform.system() != 'SunOS':
    print("Warning: This module was designed with Solaris compatibility in mind.")
  run_module()


if __name__ == '__main__':
  main()
