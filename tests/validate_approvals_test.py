import unittest
import sys, os
import os.path

# Make the application logic directory part of the python package search path so it can be imported easily
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'validate_approvals'))
from validate_approvals import ValidateApprovals

class ValidateApprovalsTest(unittest.TestCase):

    def setUp(self):
        self.v = ValidateApprovals(os.path.join(os.path.dirname(__file__), 'fixture/repo_root'))
        self.v.build_dir_maps()

    def test_build_dir_maps(self):
        self.assertEqual(self.v.dir_maps['src/com/twitter/follow'], [['src/com/twitter/user'], ['alovelace', 'ghopper']])
        self.assertEqual(self.v.dir_maps['.'], [[], ['ghopper']])
        self.assertEqual(self.v.dir_maps['src/com/twitter'], [[], []])
        self.assertEqual(
            self.v.dir_maps['tests/com/twitter/message'],
            [
                ['src/com/twitter/follow', 'src/com/twitter/message', 'src/com/twitter/user'], ['eclarke', 'kantonelli']
            ]
        )
        self.assertEqual(self.v.dir_maps['tests'], [[], []])

    def test_get_dir_all_owners(self):
        self.assertEqual(self.v.get_dir_all_owners('.'), {'ghopper'})
        self.assertEqual(self.v.get_dir_all_owners('src/com/twitter/user'), {'ghopper'})
        self.assertEqual(self.v.get_dir_all_owners('src/com/twitter/message'), {'ghopper', 'eclarke', 'kantonelli'})
        self.assertEqual(self.v.get_dir_all_owners('tests/com/twitter/follow'), {'ghopper', 'alovelace'})
        
    def test_get_dir_upstream_deps(self):
        self.assertEqual(self.v.get_dir_upstream_deps('.'), ['.'])
        self.assertEqual(sorted(self.v.get_dir_upstream_deps('src/com/twitter/user')),
            sorted([
                'src/com/twitter/user',
                'src/com/twitter/message',
                'src/com/twitter/tweet',
                'src/com/twitter/follow',
                'tests/com/twitter/user',
                'tests/com/twitter/message',
                'tests/com/twitter/follow'
            ]
        ))
        self.assertEqual(self.v.get_dir_upstream_deps('src/com/twitter'), ['src/com/twitter'])
        self.assertEqual(self.v.get_dir_upstream_deps('tests/com/twitter/message'), ['tests/com/twitter/message'])
        self.assertEqual(sorted(self.v.get_dir_upstream_deps('src/com/twitter/tweet')),
            sorted(['src/com/twitter/tweet', 'tests/com/twitter/tweet']
        ))
        self.assertEqual(sorted(self.v.get_dir_upstream_deps('src/com/twitter/follow')),
            sorted([
                'src/com/twitter/follow',
                'src/com/twitter/message',
                'src/com/twitter/tweet',
                'tests/com/twitter/follow',
                'tests/com/twitter/message',
                'tests/com/twitter/tweet'
            ]
        ))

    def test_validate_approvals(self):
        normalized_path = os.path.join(os.path.dirname(__file__), 'fixture/repo_root')
        v1 = ValidateApprovals(normalized_path, 'alovelace,ghopper', 'src/com/twitter/follow/Follow.java,src/com/twitter/user/User.java')
        self.assertTrue(v1.validate_approvals())

        v2 = ValidateApprovals(normalized_path, 'alovelace', 'src/com/twitter/follow/Follow.java')
        self.assertFalse(v2.validate_approvals())

        v3 = ValidateApprovals(normalized_path,  'eclarke', 'src/com/twitter/follow/Follow.java')
        self.assertFalse(v3.validate_approvals())

        v4 = ValidateApprovals(normalized_path, 'alovelace,eclarke', 'src/com/twitter/follow/Follow.java')
        self.assertTrue(v4.validate_approvals())

        v5 = ValidateApprovals(normalized_path, 'mfox', 'src/com/twitter/tweet/Tweet.java')
        self.assertTrue(v5.validate_approvals())

        v6 = ValidateApprovals(normalized_path, 'ghopper', 'tests/com/twitter/tweet/UserTest.java')
        self.assertTrue(v6.validate_approvals())

        v7 = ValidateApprovals(normalized_path, 'alovelace', 'src/com/twitter/follow/DEPENDENCIES')
        self.assertFalse(v7.validate_approvals())

        v8 = ValidateApprovals(normalized_path, 'eclarke,kantonelli', 'src/com/twitter/message/OWNERS')
        self.assertTrue(v8.validate_approvals())

        v9 = ValidateApprovals(normalized_path, 'ghopper', './OWNERS')
        self.assertTrue(v9.validate_approvals())

        v10 = ValidateApprovals(normalized_path, 'eclarke', 'src/com/twitter/tweet/Message.java')
        self.assertFalse(v10.validate_approvals())

        v11 = ValidateApprovals(normalized_path, 'kantonelli,eclarke', 'src/com/twitter/tweet/User.java')
        self.assertFalse(v11.validate_approvals())

if __name__ == '__main__':
    unittest.main(verbosity=2)