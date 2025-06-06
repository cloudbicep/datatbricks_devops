# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # 2.6 - Performing Integration Tests
# MAGIC
# MAGIC Integration tests for data engineering ensures that different components of the data pipeline, such as data ingestion, transformation, storage, and retrieval, work together seamlessly in a real-world environment. These tests validate the flow of data across systems, checking for issues like data consistency, format mismatches, and processing errors when components interact as expected.
# MAGIC
# MAGIC There are multiple ways to implement integration tests within Databricks:
# MAGIC
# MAGIC 1. **Delta Live Tables (DLT)**: With DLT, you can use expectations to check pipeline’s results.
# MAGIC     - [Manage data quality with pipeline expectations](https://docs.databricks.com/en/delta-live-tables/expectations.html#manage-data-quality-with-pipeline-expectations)
# MAGIC
# MAGIC 2. **Workflow Tasks**: You can also perform integration tests as a Databricks Workflow with tasks - similarly what is typically done for non-DLT code.
# MAGIC
# MAGIC In this demonstration, we will quickly introduce to you how to perform simple integration tests with Delta Live Tables and discuss how to implement them with Workflows. Prior knowledge of DLT and Workflows is assumed.
# MAGIC
# MAGIC ## Objectives
# MAGIC
# MAGIC - Learn how to perform integration testing in DLT pipelines using expectations.
# MAGIC - Understand how to perform integration tests on data from DLT pipelines using Workflow tasks.

# COMMAND ----------

# MAGIC %md
# MAGIC ## REQUIRED - SELECT CLASSIC COMPUTE
# MAGIC
# MAGIC Before executing cells in this notebook, please select your classic compute cluster in the lab. Be aware that **Serverless** is enabled by default.
# MAGIC
# MAGIC Follow these steps to select the classic compute cluster:
# MAGIC
# MAGIC 1. Navigate to the top-right of this notebook and click the drop-down menu to select your cluster. By default, the notebook will use **Serverless**.
# MAGIC
# MAGIC 1. If your cluster is available, select it and continue to the next cell. If the cluster is not shown:
# MAGIC
# MAGIC   - In the drop-down, select **More**.
# MAGIC
# MAGIC   - In the **Attach to an existing compute resource** pop-up, select the first drop-down. You will see a unique cluster name in that drop-down. Please select that cluster.
# MAGIC
# MAGIC **NOTE:** If your cluster has terminated, you might need to restart it in order to select it. To do this:
# MAGIC
# MAGIC 1. Right-click on **Compute** in the left navigation pane and select *Open in new tab*.
# MAGIC
# MAGIC 1. Find the triangle icon to the right of your compute cluster name and click it.
# MAGIC
# MAGIC 1. Wait a few minutes for the cluster to start.
# MAGIC
# MAGIC 1. Once the cluster is running, complete the steps above to select your cluster.

# COMMAND ----------

# MAGIC %md
# MAGIC ## A. Classroom Setup
# MAGIC
# MAGIC Run the following cell to configure your working environment for this course. 
# MAGIC
# MAGIC **NOTE:** The `DA` object is only used in Databricks Academy courses and is not available outside of these courses. It will dynamically reference the information needed to run the course.
# MAGIC
# MAGIC ##### The notebook "2.1 - Modularizing PySpark Code - Required" sets up the catalogs for this course. If you have not run this notebook, the catalogs will not be available.

# COMMAND ----------

# DBTITLE 1,Setup
# MAGIC %run ../Includes/Classroom-Setup-2.6

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Option 1 - Delta Live Tables (DLT) Pipeline with Integration Tests
# MAGIC
# MAGIC In this section, we will create a DLT pipeline using the modularized functions from the `src.helpers` file, which we unit tested in the previous notebook. In the DLT pipeline, we will use these functions to create tables and then implement some simple integration tests for the output tables in our ETL pipeline for this project.
# MAGIC
# MAGIC - With DLT, you can use expectations to check pipeline’s results.
# MAGIC   - [Manage data quality with pipeline expectations](https://docs.databricks.com/en/delta-live-tables/expectations.html#manage-data-quality-with-pipeline-expectations)
# MAGIC
# MAGIC   - [Expectation recommendations and advanced patterns](https://docs.databricks.com/en/delta-live-tables/expectation-patterns.html#expectation-recommendations-and-advanced-patterns)
# MAGIC
# MAGIC   - [Applying software development & DevOps best practices to Delta Live Table pipelines](https://www.databricks.com/blog/applying-software-development-devops-best-practices-delta-live-table-pipelines)
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC 1. We will create the DLT pipeline for this project using the Databricks Academy **`DAPipelineConfig`** class, which was specifically designed for this course with the Databricks SDK. This avoids manually creating the DLT pipeline for this demo. Typically during development you would manually build the DLT pipeline with the UI during development.
# MAGIC
# MAGIC     **NOTE:** The Databricks SDK is outside the scope of this course. However, if you're interested in seeing the code that uses the SDK to automate building DLT pipelines in Databricks Academy, check out the **[../Includes/Classroom-Setup-Common]($../Includes/Classroom-Setup-Common)** notebook in **Cell 6**.
# MAGIC
# MAGIC     [Databricks SDK for Python](https://docs.databricks.com/en/dev-tools/sdk-python.html)
# MAGIC
# MAGIC     [Databricks SDK Documentation](https://databricks-sdk-py.readthedocs.io/en/latest/)
# MAGIC
# MAGIC
# MAGIC ![Full DLT Pipeline](../Includes/images/04_dlt_pipeline.png)

# COMMAND ----------

# Create the DLT pipeline for this project using the custom Databricks Academy class DAPipelineConfig that was created using the Databricks SDK. 

pipeline = DAPipelineConfig(pipeline_name=f"sdk_health_etl_{DA.catalog_dev}", 
                            catalog=f"{DA.catalog_dev}",
                            schema="default", 
                            pipeline_notebooks=[
                                "/src/dlt_pipelines/ingest-bronze-silver_dlt", 
                                "/src/dlt_pipelines/gold_tables_dlt",
                                "/tests/integration_test/integration_tests_dlt"
                              ],
                            config_variables={
                                'target':'development', 
                                'raw_data_path': f'/Volumes/{DA.catalog_dev}/default/health'
                              }
                          )

pipeline.create_dlt_pipeline()

pipeline.start_dlt_pipeline()

# COMMAND ----------

# MAGIC %md
# MAGIC 2. While the DLT pipeline is running, examine it through the UI by completing the following steps:
# MAGIC
# MAGIC    a. In the far left navigation pane, right-click on **Pipelines** and select *Open in a New Tab*.
# MAGIC
# MAGIC    b. Find your DLT pipeline named **sdk_health_etl_your_catalog_1_dev** and select it.
# MAGIC
# MAGIC    c. Click **Settings** at the top right.
# MAGIC
# MAGIC     - c1. In the **General** section notice that this DLT pipeline is using **Serverless** compute.
# MAGIC
# MAGIC     - c2. Scroll down to the **Advanced** section. You'll notice that the pipeline contains two **Configuration** variables:
# MAGIC
# MAGIC       - **target** = *'development'*
# MAGIC         - This `target` variable will be modified dynamically for each deployment to **development**, **stage**, and **production**.
# MAGIC
# MAGIC       - **raw_data_path** = *'/Volumes/your_catalog_1_dev/default/health'*
# MAGIC         - This `raw_data_path` variable will be modified dynamically for each deployment to **development data**, **stage data**, and **production data**.
# MAGIC
# MAGIC     - c3. Click **Cancel** at the bottom right.
# MAGIC
# MAGIC    d. At the top of the Pipelines select the kebab menu (three ellipses) and select **View settings YAML**. Notice that the UI provides the necessary YAML files for future deployment. We will talk more about this later. 
# MAGIC
# MAGIC    e. In the **Pipeline details** section on the far right, you should see three notebooks being used for the **Source code**. Right-click each notebook and select *Open Link in New Tab* to examine them:
# MAGIC
# MAGIC     - **Notebook 1: [..../src/dlt_pipelines/ingest-bronze-silver_dlt]($../../src/dlt_pipelines/ingest-bronze-silver_dlt)** - Obtains the DLT configuration variables that setup the target and raw data, and creates the bronze and silver tables based on those variable values.
# MAGIC   
# MAGIC     - **Notebook 2: [..../src/dlt_pipelines/gold_tables_dlt]($../../src/dlt_pipelines/gold_tables_dlt)** - Creates the gold table.
# MAGIC   
# MAGIC     - **Notebook 3: [..../tests/integration_test/integration_tests_dlt]($../../tests/integration_test/integration_tests_dlt)** - Performs simple integration tests on the bronze, silver and gold tables based on the target environment.
# MAGIC
# MAGIC    h. Here is a diagram of the entire DLT pipeline for **development, stage and production**. Depending on the values of the **target** and **raw_data_path** configuration variables that are set, the ingest data source and integration tests will vary (dev catalog, stage catalog, prod catalog), but the ETL pipeline will remain the same.
# MAGIC
# MAGIC   ![Explain DLT Pipeline]( ../Includes/images/04_dlt_explain_integrations.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Option 2 - Integration Testing with Notebooks and Databricks Workflows
# MAGIC You can also perform integration testing using notebooks and add them as tasks in jobs for your pipeline. 
# MAGIC
# MAGIC **NOTE:** We will simply review how to implement integration tests with Workflows if that is the method you prefer. The final deployment for this course uses the DLT integration tests with expectations.
# MAGIC
# MAGIC #### Steps to take:
# MAGIC 1. Create a setup notebook to handle any dynamic setup required using job parameters for your target environment and data locations.
# MAGIC
# MAGIC 2. Create additional notebooks or files to store the integration tests you want to run as tasks.
# MAGIC
# MAGIC 3. Organize the new notebooks or files within your **tests** folder.
# MAGIC
# MAGIC 4. Create a Workflow. Within the Workflow:
# MAGIC
# MAGIC    - a. Create the necessary tables or views using DLT or code.
# MAGIC
# MAGIC    - b. Add tasks to set up your integration tests (e.g., setting up any dynamic job parameters that need to be set).
# MAGIC
# MAGIC    - c. Perform validation by using your notebooks as tasks and set the tasks to all should succeed.
# MAGIC
# MAGIC **NOTES:** One major drawback of this approach is that you will need to write more code for setup and validation tasks, as well as manage the job parameters to dynamically modify the code based on the target environment.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC Integration testing can be performed in a variety of ways within Databricks. In this demonstration, we focused on how to perform simple integration tests using DLT expectations. We also discussed how to implement them with Workflow tasks.
# MAGIC
# MAGIC Depending on your specific situation, you can choose the approach that best fits your needs.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the 
# MAGIC <a href="https://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/">Support</a>
