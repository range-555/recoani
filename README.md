
# 概要
入力されたアニメタイトルを元に、あらすじが類似するアニメタイトルを出力するアプリrecoani.netのリポジトリです。

### 各リポジトリの概要
- recoani_web
<br>メインのrecoaniアプリケーションです。inputページでの入力タイトル・件数が正常であればresultページを、不正な入力であればinputページにredirectします。

- recoani_batch(calc)
<br>全アニメに対しあらすじが類似するアニメを算出し、データをDBに格納します。類似度はtf-idfにより計算しています。
- recoani_batch(collect_data)
<br>定期的にデータを収集し、DBに格納するクローラーです

# 機能

### アプリケーション本体
- 入力補助機能
- 入力タイトルに基づくアニメレコメンド機能
- 詳細(あらすじ)表示機能

### バッチ
- データ収集機能
- あらすじ類似アニメ計算機能

# 使用技術

### 構成図
![recoani_architecture](https://user-images.githubusercontent.com/50847558/84721067-babdcc00-afba-11ea-8aff-ab874134d86b.png)


### 技術一覧
#### サーバー
- AWS(EC2, RDS, Route53)
- GCP(GCE)

#### 使用言語
- Python
- HTML5 & CSS3 & jQuery

#### フレームワーク・ライブラリ
- Django
- MySQL

#### その他ツール
- Github
- Docker

### 使用技術詳細
EC2にてrecoaniアプリケーションを、GCEにてバッチを動かしています。<br>
EC2側はdocker-composeでnginx, web(django), https-portalコンテナを起動しています。<br>
GCE側ではcollect_data環境をdocker-composeで、calc環境をpyenvで構築しています。<br>
GCEからRDSへはautosshでEC2を踏み台にポートフォワードで接続しています。<br>
Route53でドメインの名前解決をしています。
<br>無料枠に収めるためにこのような構成になりましたが、基本的にAWSかGCPのどちらかのみで立てることが望ましいと実感しました。

### CMD
docker run -p 8080:8080 --env-file=./docker/collect/.env collect

docker build -t collect -f ./docker/collect/Dockerfile .


### 課題
- フリーワード検索
- シリアス・ネガティブの感情分析によるレコメンド
- 協調フィルタリング(コンテンツベースの限界)

This software includes the work that is distributed in the Apache License 2.0