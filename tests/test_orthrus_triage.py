import unittest
from orthrus.commands import *
from orthrusutils.orthrusutils import *

class TestOrthrusTriage(unittest.TestCase):

    description = 'Test harness'
    orthrusdirname = '.orthrus'
    config = {'orthrus': {'directory': orthrusdirname}}
    abconf_file = orthrusdirname + '/conf/abconf.conf'

    def test_triage(self):
        args = parse_cmdline(self.description, ['triage', '-j', self.add_cmd.job.id])
        cmd = OrthrusTriage(args, self.config, test=True)
        self.assertTrue(cmd.run())

    def test_triage_abtest(self):
        args = parse_cmdline(self.description, ['triage', '-j', self.add_cmd_abtest.job.id])
        cmd = OrthrusTriage(args, self.config, test=True)
        self.assertTrue(cmd.run())

    @classmethod
    def setUpClass(cls):
        # Create
        args = parse_cmdline(cls.description, ['create', '-asan'])
        cmd = OrthrusCreate(args, cls.config)
        cmd.run()
        # Add routine job
        args = parse_cmdline(cls.description, ['add', '--job=main @@',
                                                '-s=./seeds'])
        cls.add_cmd = OrthrusAdd(args, cls.config)
        cls.add_cmd.run()
        # Start routine job fuzzing
        args = parse_cmdline(cls.description, ['start', '-j', cls.add_cmd.job.id])
        cmd = OrthrusStart(args, cls.config)
        cmd.run()
        time.sleep(2*TEST_SLEEP)
        # Stop routine job fuzzing
        args = parse_cmdline(cls.description, ['stop', '-j', cls.add_cmd.job.id])
        cmd = OrthrusStop(args, cls.config)
        cmd.run()
        # Add a/b test job
        abconf_dict = {'fuzzerA': 'afl-fuzz', 'fuzzerA_args': '', 'fuzzerB': 'afl-fuzz-fast', 'fuzzerB_args': ''}
        with open(cls.abconf_file, 'w') as abconf_fp:
            json.dump(abconf_dict, abconf_fp, indent=4)
        args = parse_cmdline(cls.description, ['add', '--job=main @@', '-s=./seeds', '--abconf={}'.
                             format(cls.abconf_file)])
        cls.add_cmd_abtest = OrthrusAdd(args, cls.config)
        cls.add_cmd_abtest.run()
        # Start a/b test job
        args = parse_cmdline(cls.description, ['start', '-j', cls.add_cmd_abtest.job.id])
        cmd = OrthrusStart(args, cls.config)
        cmd.run()
        time.sleep(2 * TEST_SLEEP)
        # Stop a/b test job
        args = parse_cmdline(cls.description, ['stop', '-j', cls.add_cmd_abtest.job.id])
        cmd = OrthrusStop(args, cls.config)
        cmd.run()
        # Simulate old triage
        sim_unique_dir = cls.orthrusdirname + '/jobs/abtests/{}/{}/unique'.format(cls.add_cmd_abtest.job.id,
                                                                         cls.add_cmd_abtest.job.joba_id)
        if not os.path.isdir(sim_unique_dir):
            os.mkdir(sim_unique_dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.orthrusdirname)