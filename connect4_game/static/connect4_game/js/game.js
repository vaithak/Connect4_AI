angular.module('connectFour', ['luegg.directives'])
.factory('socket', function() {
    var stack = [];
    var onmessageDefer;
    var socket = {
        ws: new ReconnectingWebSocket(ws_scheme + window.location.host + '/ws/game/' + roomName + '/'),
        send: function(data) {
            data = JSON.stringify(data);
            if (socket.ws.readyState == 1) {
                socket.ws.send(data);
            } else {
                stack.push(data);
            }
        },
        onmessage: function(callback) {
            if (socket.ws.readyState == 1) {
                socket.ws.onmessage = callback;
            } else {
                onmessageDefer = callback;
            }
        }
    };

    if (!socket.ws.readyState === WebSocket.CLOSED)
        socket.ws.close();

    socket.ws.onopen = function(event){
        socket.ws.send(JSON.stringify({'command': 'fetch_state' }));

        if (onmessageDefer) {
            socket.ws.onmessage = onmessageDefer;
            onmessageDefer = null;
        }
    };
    // socket.ws.onopen = function(event) {
    //     for (i in stack) {
    //         socket.ws.send(stack[i]);
    //     }
    //     stack = [];
    //     if (onmessageDefer) {
    //         socket.ws.onmessage = onmessageDefer;
    //         onmessageDefer = null;
    //     }
    // };
    return socket;
})
.controller('mainController', ['$scope', '$http', '$timeout', 'socket', function($scope, $http, $timeout, socket) {

    var vm = this;

    vm.init = function() {
        vm.boardState = [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0]
        ];

        vm.active = 'r';

        vm.dropAllowed = false;

        vm.winner = false;

        // vm.aiComments = ['Once you start playing, the AI will tell you why it\'s using specific moves here.'];
    };
    
    vm.onmessage = function(event) {
        var data = JSON.parse(event.data);

        // simulating drop
        data = data['message'];
        if(data['command']=='new_state' && data['state']['prev_player'] != username){
            vm.dropAllowed = true;
            var index  = parseInt(data['state']['index']);
            var index2 = parseInt(data['state']['index2']);
            vm.drop(index, index2, false, function(){
                data = data['state'];
                vm.dropAllowed = (data['new_player'] == username);
                vm.active = data['active'];
                if(data['is_finished'] == true){
                    if(vm.active == 'r') {vm.winner = "yellow";}
                    else {vm.winner= "red";}
                }
                else{ vm.winner = false; }
                if(vm.winner){
                    vm.dropAllowed = false;
                }
                let tempBoardState = data['state'].split('');
                for(let i=0; i<vm.boardState.length; i = i+1){
                    for(let j=0; j<vm.boardState[i].length; j=j+1){
                        if(tempBoardState[i*vm.boardState[i].length + j] == '0' && vm.boardState[i][j]!=0)
                            vm.boardState[i][j] = 0;
                        else if(vm.boardState[i][j]!=tempBoardState[i*vm.boardState[i].length + j])
                            vm.boardState[i][j] = tempBoardState[i*vm.boardState[i].length + j];
                    }
                }
            });
        }
        // now updating other data
        else{
            data = data['state'];
            vm.dropAllowed = (data['new_player'] == username);
            vm.active = data['active'];
            if(data['is_finished'] == true){
                if(vm.active == 'r') {vm.winner = "yellow";}
                else {vm.winner= "red";}
            }
            else{ vm.winner = false; }
            
            if(vm.winner){
                vm.dropAllowed = false;
            }
            let tempBoardState = data['state'].split('');
            for(let i=0; i<vm.boardState.length; i = i+1){
                for(let j=0; j<vm.boardState[i].length; j=j+1){
                    if(tempBoardState[i*vm.boardState[i].length + j] == '0' && vm.boardState[i][j]!=0)
                        vm.boardState[i][j] = 0;
                    else if(vm.boardState[i][j]!=tempBoardState[i*vm.boardState[i].length + j])
                        vm.boardState[i][j] = tempBoardState[i*vm.boardState[i].length + j];
                }
            }
        }

        $scope.$digest();
    };

    socket.onmessage(vm.onmessage);

    vm.init();

    vm.playType = 1;

    vm.modal = false;

    vm.drop = function(index, index2, curr_bool, callback) {
        if (vm.dropAllowed && vm.boardState[index][index2] === 0) {
            vm.dropAllowed = false;
            vm.boardState[0][index2] = vm.active;
            //recursive timeout loop
            (function dropLoop(i) {
                $timeout(function() {
                    if (typeof vm.boardState[i] !== 'undefined' && vm.boardState[i][index2] === 0 && i <= 5) {
                        vm.boardState[i - 1][index2] = 0;
                        vm.boardState[i][index2] = vm.active;
                        dropLoop(i + 1);
                    } else {
                        if(curr_bool == true){
                            socket.send({
                                'command': 'new_state',
                                'state': (vm.boardState).map(e => e.join('')).join(''),
                                'index': index,
                                'index2': index2,
                            });
                        }
                        if (typeof(callback) !== 'undefined'){
                            callback();
                        }
                    }
                }, 50);
            })(1);
        }
    };

    vm.reset = function(){
        socket.send({'command': 'reset_state' });
    };

}]);