cd antlr
& java -cp ..\..\..\antlr-4.9.2-complete.jar org.antlr.v4.Tool Cool.g4
& "N:\Program Files\Java\jdk-17\bin\javac" -cp ..\..\..\antlr-4.9.2-complete.jar *.java
& "N:\Program Files\Java\jdk-17\bin\java" -cp ".;..\..\..\antlr-4.9.2-complete.jar" org.antlr.v4.gui.TestRig Cool program -gui
cd ..
