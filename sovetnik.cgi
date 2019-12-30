#!/bin/sh

_BASE_DIR="."

log () {

	# Раскомментируй для логирования
	#echo "$(date): $*" >> $_BASE_DIR/sovetnik.log
	return

}

log "Got message"

if [ "$REQUEST_METHOD" = "POST" ] && [ $CONTENT_LENGTH -gt 0 ]; then

	# Прочитали POST
	QUERY_STRING_POST=$(cat)

	_PARSED=$(echo "$QUERY_STRING_POST" | sed "s/ \\\n/\\\\\\\n/g")

	# jq на роутер лень собирать :)
	_PARSED=$(echo -e "$_PARSED" | $_BASE_DIR/JSON.awk)

	_CHAT_ID=$(echo -e "$_PARSED" | grep '\["message","chat","id"\]' | sed 's/.*\t\(.*\)/\1/')
	_CHAT_TYPE=$(echo -e "$_PARSED" | grep '\["message","chat","type"\]' | sed 's/.*\t"\(.*\)"/\1/')
	
	_MESSAGE=$(echo -e "$_PARSED" | grep '\["message","text"\]' | sed 's/.*\t"\(.*\)"/\1/')

	# для разворачивания \uXXXX в нормальный UTF-8
	_QUERY=$(printf "$_MESSAGE")

	log "Query: $_QUERY"

	# Костыль из-за проблем с UTF-8
	_QUERY=$(echo "$_QUERY" | sed -f $_BASE_DIR/lowercase.sed)

	# Триггеримся только на определённую форму фразы, извлекаем термин и выкидываем запятые, если есть
	_TERM=$(echo "$_QUERY" | grep -i "а что иль кто есть .* советник?" | sed 's/а что иль кто есть \(.*\) советник?/\1/Ig' | sed 's/,//g')

	log "Term: $_TERM"

	# Это не нам, просто молчим в тряпочку
	if [ "$_TERM" = "" ]; then
		exit 0;
	fi

	_DICT_FILE=$_BASE_DIR/dicts/dict

	# grep'нули все строки по термину
	_LINE=$(grep -i "$_TERM::" $_DICT_FILE)

	log "Lines: $_LINE"

	# Выбрали одну случайную
	_LINE=$(echo "$_LINE" | awk 'BEGIN{srand() }
	{ lines[++d]=$0 }
	END{
		RANDOM = int(1 + rand() * d)
	    print lines[RANDOM]
	}')

	log "Selected line: $_LINE"

	# Выкинули сам термин, оставив только ответ
	_ANSWER=$(echo "$_LINE" | sed 's/.*::/\1/')

	# Если ответ не найден
	if [ "$_ANSWER" = "" ]; then
		_ANSWER="Про то мне ничего не известно, колесник."
	fi

	echo -en "Content-Type: application/json; charset=UTF-8\r\n\r\n";

	# В личку отвечаем как есть, в группу - ответом на сообщение
	if [ "$_CHAT_TYPE" = "private" ]; then
		_JSON="{\"method\": \"sendMessage\", \"chat_id\": $_CHAT_ID, \"text\": \"$_ANSWER\"}"
	else
		_MESSAGE_ID=$(echo -e "$_PARSED" | grep '\["message","message_id"\]' | sed 's/.*\t\(.*\)/\1/')
		_JSON="{\"method\": \"sendMessage\", \"chat_id\": $_CHAT_ID, \"reply_to_message_id\": $_MESSAGE_ID, \"text\": \"$_ANSWER\"}"
	fi

	log "$_JSON"

	echo "$_JSON"

fi
