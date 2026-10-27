FLAGS=-fno-stack-protector -no-pie -g

all:
	@echo "Usage: make EXERCISE_NAME"

clean:
	rm -rf ./bin

%:
	@mkdir -p bin
	gcc $@.c -o ./bin/$@ ${FLAGS}
