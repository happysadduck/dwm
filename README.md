# DWM
(DeepSeek-based Words Memorizor)基于ds的背单词软件.

## 导入单词
- 使用UTF-8格式的.csv存储单词表. 
- 文件必须是./wordlist/vocab.csv
- 必须要有一个表头"word,meaning"
- 下面部分用逗号分隔, 左边英文词, 右边写中文(也可以包括词性, 多个示意, 甚至音标, 但是就是不能有逗号)
例如:
```csv
word,meaning
abandon,v. 抛弃，放弃 离弃(家园、船只、飞机等) 遗弃(妻、子女等)
```

## 设置
设置是./config/settings.json
- "daily_new_words" 表示一日新学的单词数
- "daily_review_words" 表示一日复习的单词数
- "review_words_growth_days" 表示过多少天复习单词数就会+1, 这一点会直接更新上面那一条设置(赤石)
- "forgetting_curve_halflife" 单词记忆的半衰期(你觉得你过多久就会只记得一半单词, 记性越好数值越大, 推荐3.0)

developing...