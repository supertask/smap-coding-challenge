# -*- coding: utf-8 -*-

class Util:
    @classmethod
    def split_list(self, target_list, segment_len):
        """リストをサブリストに分割する
        """
        return [
          target_list[i : i + segment_len]
          for i in range(0, len(target_list), segment_len)
        ]