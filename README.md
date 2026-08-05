# X keyword → Discord monitor

5分ごとに Bing のWeb検索を使って

`site:x.com "ヴァン" "真斗" "メセカ"`

を確認し、新しい X の検索結果が見つかった場合だけ Discord Webhook に通知します。

## 大事な注意

- X公式APIは使わないので無料です。
- Xを直接監視しているわけではありません。検索エンジンに載るまで遅れたり、投稿が検索結果に出ないことがあります。
- GitHub Actionsの `*/5` は「最短5分間隔」ですが、GitHub側の混雑で実行が遅れることがあります。
- 最初の1回は、その時点ですでに存在する検索結果を「既読」にするだけで通知しません。

## GitHubでの設定

1. GitHubで新しいリポジトリを作ります。**Private推奨**。
2. このフォルダ内のファイルをそのリポジトリへアップロードします。
3. Discordで通知したいサーバーを開きます。
4. `サーバー設定 → 連携サービス → ウェブフック → 新しいウェブフック` で作成します。
5. 通知先チャンネルを選び、Webhook URLをコピーします。
6. GitHubのリポジトリで
   `Settings → Secrets and variables → Actions → New repository secret`
   を開きます。
7. Name を `DISCORD_WEBHOOK_URL` にして、Secret にDiscordのWebhook URLを貼り付けます。
8. GitHubの `Actions` タブ → `X keyword monitor` → `Run workflow` を1回実行します。
9. 初回が成功したら、その後は約5分おきに自動チェックします。

## テスト方法

初回実行では通知しない仕様です。
Discordへの疎通だけ試したい場合は、一時的に `seen.json` を削除するのではなく、
`monitor.py` の検索語をテスト用の珍しい語に変えるなどして確認してください。

## Webhook URLについて

Discord Webhook URLはパスワード同様に扱ってください。
コードや公開リポジトリに直接貼らず、必ずGitHub Secretsに保存してください。
