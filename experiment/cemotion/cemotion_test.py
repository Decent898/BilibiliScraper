from cemotion import Cegmentor
from cemotion import Cemotion

segmenter = Cegmentor()

text1 = '这辆车的内饰设计非常现代，而且用料考究，给人一种豪华的感觉。'
segmentation_result = segmenter.segment(text1)
print(segmentation_result)

text2 = '我非常喜欢这家餐厅的菜品，尤其是他们的招牌菜，味道非常棒。'

segmentation_result = segmenter.segment(text2)
print(segmentation_result)



str_text1 = '配置顶级，不解释，手机需要的各个方面都很完美'
str_text2 = '院线看电影这么多年以来，这是我第一次看电影睡着了。简直是史上最大烂片！没有之一！侮辱智商！大家小心警惕！千万不要上当！再也不要看了！'

c = Cemotion()
print(f'"{str_text1}"\nPredicted value:{c.predict(str_text1)}\n')
print(f'"{str_text2}"\nPredicted value:{c.predict(str_text2)}\n')