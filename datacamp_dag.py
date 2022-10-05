from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.sensors.filesystem import FileSensor
from datetime import timedelta 
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator


default_args = {
    'start_date': days_ago(1),
    'owner':'vale',
    'email':'viniciusdvale@gmail.com',
    'email_on_failure':False,
    'email_on_retry:': False,
    'email_on_success':False

}

echo_templated = """ echo "Reading {{ params.filename }}"
"""
for_templated = """ {% for filename in params.filenames %}
echo "Writing {{ filename }}"
{% endfor %}

"""

def branch_date(ds_nodash):
    if int(ds_nodash) % 2 == 0:
        return 'rand_number'
    return 'stop_dag'

@dag(schedule_interval=None, default_args=default_args, catchup=False, tags=['datacamp'])
def datacamp_dag():
    rand_number = BashOperator(task_id='rand_number',bash_command='echo $RANDOM')
    echo_ex = BashOperator(task_id='echo_ex',bash_command='echo "Exemple!"')
    echo_template = BashOperator(task_id='echo_template',bash_command=echo_templated, params={'filename':'salesdata.csv'})
    echo_for = BashOperator(task_id='echo_for',bash_command=for_templated, params={'filenames':['sales.text','data.out']},trigger_rule="all_done")


    @task
    def printme():
        print("This goes in the logs!")

    @task
    def sleep(lenght_time):
        import time
        time.sleep(lenght_time)

    email_task = EmailOperator(task_id='Notify', to='viniciusdvale@gmail.com', subject='Datacamp dag sleep well', html_content='<p>Time to wake up little Dag<p>',)
    salesdata_sensor = FileSensor(task_id='pock_salesdata',filepath='salesdata.csv',poke_interval=30, timeout=60*5, mode='reschedule')
    isrunday = BranchPythonOperator(task_id='isrunday',python_callable=branch_date)
    stop_dag = EmptyOperator(task_id='stop_dag')

    t_pintme = printme()
    t_sleep = sleep(5)

    isrunday >> [rand_number,stop_dag]
    rand_number >> [echo_ex, t_pintme] >> t_sleep >> email_task >> [salesdata_sensor,echo_template] >> echo_for

dag = datacamp_dag()