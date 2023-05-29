def test_function():
    from some_dags.functions import print_success

    assert print_success() == "SUCCESSFUL !"


def test_dag():
    from some_dags.my_dag import dag

    assert dag
