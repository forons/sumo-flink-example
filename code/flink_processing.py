from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings


def flink_processing():
    # 1. create a TableEnvironment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    env_settings = EnvironmentSettings.Builder().use_blink_planner().build()
    t_env = StreamTableEnvironment.create(stream_execution_environment=env,
                                          environment_settings=env_settings)
    # specify connector and format jars
    t_env.get_config().get_configuration().set_string(
        "pipeline.jars",
        "file:////<PATH TO>/flink-connector-kafka_2.11-1.12.0.jar;"
        "file:////<PATH TO>/flink-sql-connector-kafka_2.11-1.12.0.jar"
    )

    # Define the data that are going to be read from kafka
    source_ddl = """
                    CREATE TABLE source_num(
                      `ts` TIMESTAMP(3) METADATA FROM 'timestamp',
                      `step` FLOAT,
                      `edge_id` STRING,
                      `vehicle_num` INT
                    ) WITH (
                      'connector' = 'kafka',
                      'topic' = 'source_num',
                      'properties.bootstrap.servers' = 'localhost:9092',
                      'properties.group.id' = 'new_group2',
                      'format' = 'json'
                    )
                    """

    # Define the data that are going to be written to kafka,
    # after the processing
    sink_ddl = """
                    CREATE TABLE sink_table_num(
                        `ts` TIMESTAMP(3) METADATA FROM 'timestamp',
                        `step` FLOAT,
                        `edge_id` STRING,
                        `vehicle_num` INT
                    ) WITH (
                      'connector' = 'kafka',
                      'topic' = 'sink_topic_num',
                      'properties.bootstrap.servers' = 'localhost:9092',
                      'format' = 'json'
                    )
                    """

    # Actually create the two tables
    t_env.execute_sql(source_ddl)
    t_env.execute_sql(sink_ddl)

    # Execute the wanted query
    t_env.sql_query(
        "SELECT `ts`, `step`, `edge_id`, `vehicle_num` "
        "FROM `source_num` "
        "WHERE `edge_id`='172515808' OR `edge_id`='-29458641'"
    ).execute_insert("sink_table_num").wait()


if __name__ == "__main__":
    flink_processing()
