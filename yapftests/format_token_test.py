# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for yapf.format_token."""

import unittest

from yapf_third_party._ylib2to3 import pytree, pygram
from yapf_third_party._ylib2to3.pgen2 import token

from yapf.yapflib import format_token
from yapf.pytree import subtype_assigner

from yapftests import yapf_test_helper


class TabbedContinuationAlignPaddingTest(yapf_test_helper.YAPFTest):

  def testSpace(self):
    align_style = 'SPACE'

    pad = format_token._TabbedContinuationAlignPadding(0, align_style, 2)
    self.assertEqual(pad, '')

    pad = format_token._TabbedContinuationAlignPadding(2, align_style, 2)
    self.assertEqual(pad, ' ' * 2)

    pad = format_token._TabbedContinuationAlignPadding(5, align_style, 2)
    self.assertEqual(pad, ' ' * 5)

  def testFixed(self):
    align_style = 'FIXED'

    pad = format_token._TabbedContinuationAlignPadding(0, align_style, 4)
    self.assertEqual(pad, '')

    pad = format_token._TabbedContinuationAlignPadding(2, align_style, 4)
    self.assertEqual(pad, '\t')

    pad = format_token._TabbedContinuationAlignPadding(5, align_style, 4)
    self.assertEqual(pad, '\t' * 2)

  def testVAlignRight(self):
    align_style = 'VALIGN-RIGHT'

    pad = format_token._TabbedContinuationAlignPadding(0, align_style, 4)
    self.assertEqual(pad, '')

    pad = format_token._TabbedContinuationAlignPadding(2, align_style, 4)
    self.assertEqual(pad, '\t')

    pad = format_token._TabbedContinuationAlignPadding(4, align_style, 4)
    self.assertEqual(pad, '\t')

    pad = format_token._TabbedContinuationAlignPadding(5, align_style, 4)
    self.assertEqual(pad, '\t' * 2)


class FormatTokenTest(yapf_test_helper.YAPFTest):

  def testSimple(self):
    tok = format_token.FormatToken(
        pytree.Leaf(token.STRING, "'hello world'"), 'STRING')
    self.assertEqual(
        "FormatToken(name=DOCSTRING, value='hello world', column=0, "
        'lineno=0, splitpenalty=0)', str(tok))
    self.assertTrue(tok.is_string)

    tok = format_token.FormatToken(
        pytree.Leaf(token.COMMENT, '# A comment'), 'COMMENT')
    self.assertEqual(
        'FormatToken(name=COMMENT, value=# A comment, column=0, '
        'lineno=0, splitpenalty=0)', str(tok))
    self.assertTrue(tok.is_comment)

  def testIsMultilineString(self):
    tok = format_token.FormatToken(
        pytree.Leaf(token.STRING, '"""hello"""'), 'STRING')
    self.assertTrue(tok.is_multiline_string)

    tok = format_token.FormatToken(
        pytree.Leaf(token.STRING, 'r"""hello"""'), 'STRING')
    self.assertTrue(tok.is_multiline_string)

  #------------test argument names------------
  # fun(
  #    a='hello world',
  #    # comment,
  #    b='')
  child1 = pytree.Leaf(token.NAME, 'a')
  child2 = pytree.Leaf(token.EQUAL, '=')
  child3 = pytree.Leaf(token.STRING, "'hello world'")
  child4 = pytree.Leaf(token.COMMA, ',')
  child5 = pytree.Leaf(token.COMMENT,'# comment')
  child6 = pytree.Leaf(token.COMMA, ',')
  child7 = pytree.Leaf(token.NAME, 'b')
  child8 = pytree.Leaf(token.EQUAL, '=')
  child9 = pytree.Leaf(token.STRING, "''")
  node_type = pygram.python_grammar.symbol2number['arglist']
  node = pytree.Node(node_type, [child1, child2, child3, child4, child5,
                                child6, child7, child8,child9])
  subtype_assigner.AssignSubtypes(node)

  def testIsArgName(self, node=node):
    tok = format_token.FormatToken(node.children[0],'NAME')
    self.assertTrue(tok.is_argname)

  def testIsArgAssign(self, node=node):
    tok = format_token.FormatToken(node.children[1], 'EQUAL')
    self.assertTrue(tok.is_argassign)

  # test if comment inside is not argname
  def testCommentNotIsArgName(self, node=node):
    tok = format_token.FormatToken(node.children[4], 'COMMENT')
    self.assertFalse(tok.is_argname)

if __name__ == '__main__':
  unittest.main()
