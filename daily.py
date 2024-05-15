import pymysql


def daily(query):
     # 连接数据库
    conn = pymysql.connect(
        host='192.168.X.xx',
        user='XXX',
        password='XXXXXX',
        database='XXX',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        # 执行查询
        with conn.cursor() as cursor:
            cursor.execute(query)
             # 提交事务
            conn.commit()
            print("每日初始化任务成功")
    except Exception as e:
        print(f"发生错误: {str(e)}")

    finally:
        # 关闭连接
        conn.close()
query="UPDATE ai SET state =1 WHERE state = 2 " 
query2="DELETE FROM ai WHERE state = 4;" 
daily(query)
daily(query2)
