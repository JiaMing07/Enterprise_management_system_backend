coverage run --source eam_backend,User,Department,Asset,Request,Async -m pytest --junit-xml=xunit-reports/xunit-result.xml
ret=$?
coverage xml -o coverage-reports/coverage.xml
coverage report
exit $ret
