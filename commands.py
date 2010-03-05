if play_command == ('netty:run'):
	check_application()
	load_modules()
	do_classpath()
	do_java('play.modules.netty.Server')
	print "~ Ctrl+C to stop"
	print "~ "
	if application_mode == 'dev':
		check_jpda()
		java_cmd.insert(2, '-Xdebug')
		java_cmd.insert(2, '-Xrunjdwp:transport=dt_socket,address=%s,server=y,suspend=n' % jpda_port)
		java_cmd.insert(2, '-Dplay.debug=yes')
	subprocess.call(java_cmd, env=os.environ)
	print
	sys.exit(0)
if play_command == ('netty:test'):
    play_id = 'test'
    check_application()
    load_modules()
    do_classpath()
    disable_check_jpda = False
    if remaining_args.count('-f') == 1:
        disable_check_jpda = True
        remaining_args.remove('-f')
    do_java('play.modules.netty.Server')
    print "~ Running in test mode"
    print "~ Ctrl+C to stop"
    print "~ "
    check_jpda()
    java_cmd.insert(2, '-Xdebug')
    java_cmd.insert(2, '-Xrunjdwp:transport=dt_socket,address=%s,server=y,suspend=n' % jpda_port)
    java_cmd.insert(2, '-Dplay.debug=yes')
    subprocess.call(java_cmd, env=os.environ)
    print
    sys.exit(0)
if play_command == 'netty:auto-test':
    play_id = 'test'
    check_application()
    load_modules()
    do_classpath()
    do_java('play.modules.netty.Server')
    print "~ Running in test mode"
    print "~ Ctrl+C to stop"
    print "~ "
    print "~ Deleting %s" % os.path.normpath(os.path.join(application_path, 'tmp'))
    if os.path.exists(os.path.join(application_path, 'tmp')):
            shutil.rmtree(os.path.join(application_path, 'tmp'))
    print "~"
    test_result = os.path.join(application_path, 'test-result')
    if os.path.exists(test_result):
            shutil.rmtree(test_result)
    sout = open(os.path.join(log_path, 'system.out'), 'w')
    play_process = subprocess.Popen(java_cmd, env=os.environ, stdout=sout)
    soutint = open(os.path.join(log_path, 'system.out'), 'r')
    while True:
            if play_process.poll():
                    print "~"
                    print "~ Oops, application has not started?"
                    print "~"
                    sys.exit(-1)
            line = soutint.readline().strip()
            if line:
                    print line
                    if line.find('Listening for HTTP') > -1:
                            soutint.close()
                            break
    # Launch the browser
    print "~"
    print "~ Loading the test runner at %s ..." % ('http://localhost:%s/@tests' % http_port)
    try:
            proxy_handler = urllib2.ProxyHandler({})
            opener = urllib2.build_opener(proxy_handler)
            opener.open('http://localhost:%s/@tests' % http_port);
    except urllib2.HTTPError, e:
            print "~"
            print "~ There are compilation errors... (%s)" % (e.code)
            print "~"
            kill(play_process.pid)
            sys.exit(-1)
    print "~ Launching a web browser at http://localhost:%s/@tests?select=all&auto=yes ..." % http_port
    webbrowser.open('http://localhost:%s/@tests?select=all&auto=yes' % http_port)
    while True:
            time.sleep(1)
            if os.path.exists(os.path.join(application_path, 'test-result/result.passed')):
                    print "~"
                    print "~ All tests passed"
                    print "~"
                    kill(play_process.pid)
                    break
            if os.path.exists(os.path.join(application_path, 'test-result/result.failed')):
                    print "~"
                    print "~ Some tests have failed. See file://%s for results" % test_result
                    print "~"
                    kill(play_process.pid)
                    break
    sys.exit(0)
