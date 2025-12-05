Etape1 Installer docker

# exécusion de docker
    sudo docker compose up

```
def write_to_mysql(batch_df, batch_id):
    (
        batch_df.write
        .format("jdbc")
        .option("url", "jdbc:mysql://localhost:3306/social_stream")
        .option("dbtable", "tweets_sentiment")
        .option("user", "root")
        .option("password", "password")
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .mode("append")
        .save()
    )
```


Joseph, Imane, & Alicia TCHEMO