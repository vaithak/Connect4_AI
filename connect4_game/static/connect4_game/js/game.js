// app.factory('socket', [function() {
//     var stack = [];
//     var onmessageDefer;
//     var socket = {
//         ws: new WebSocket(websocket_url),
//         send: function(data) {
//             data = JSON.stringify(data);
//             if (socket.ws.readyState == 1) {
//                 socket.ws.send(data);
//             } else {
//                 stack.push(data);
//             }
//         },
//         onmessage: function(callback) {
//             if (socket.ws.readyState == 1) {
//                 socket.ws.onmessage = callback;
//             } else {
//                 onmessageDefer = callback;
//             }
//         }
//     };
//     socket.ws.onopen = function(event) {
//         for (i in stack) {
//             socket.ws.send(stack[i]);
//         }
//         stack = [];
//         if (onmessageDefer) {
//             socket.ws.onmessage = onmessageDefer;
//             onmessageDefer = null;
//         }
//     };
//     return socket;
// }]);

angular.module('connectFour', ['luegg.directives'])
.factory('socket', function() {
    var stack = [];
    var onmessageDefer;
    var socket = {
        ws: new WebSocket('ws://' + window.location.host + '/ws/game/' + roomName + '/'),
        send: function(data) {
            console.log(data);
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
        console.log(data);
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
                vm.winner = (data['is_finished'] == 'true');
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
            vm.winner = (data['is_finished'] == 'true');
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
                            console.log("hi");
                            callback();
                        }
                        // vm.dropAllowed = true;
                        // vm.winner = vm.winDetect();
                        // if (vm.winner) {
                        //     vm.dropAllowed = false;
                        // }
                        // if (vm.playType == 1 && vm.active == 'y') {
                        //     //ai
                        //     vm.ai();                            
                        // }
                    }
                }, 50);
            })(1);
        }
    };

}]);

/*
    To do list:
    hypothetical thinking ahead. Before the ai makes a move, see if that would put the other player in a winning position
*/


// vm.winDetect = function() {
    //     var tempWinner = false;
    //     //horiz
    //     for (var i = 0; i < vm.boardState.length; i++) {
    //         var rowMatch = vm.boardState[i].join('').match(/r{4}|y{4}/);
    //         if (rowMatch) {
    //             rowMatch[0].indexOf("r") > -1 ? tempWinner = "red" : tempWinner = "yellow";
    //         }
    //     }
    //     //vertical
    //     var columns = vm.getColumns();
    //     for (var j = 0; j < columns.length; j++) {
    //         var colMatch = columns[j].join('').match(/r{4}|y{4}/);
    //         if (colMatch) {
    //             colMatch[0].indexOf("r") > -1 ? tempWinner = "red" : tempWinner = "yellow";
    //         }
    //     }
    //     //diag
    //     var diags = vm.getDiags();
    //     for (var l = 0; l < diags.length; l++) {
    //         var diagMatch = diags[l].join('').match(/r{4}|y{4}/);
    //         if (diagMatch) {
    //             diagMatch[0].indexOf("r") > -1 ? tempWinner = "red" : tempWinner = "yellow";
    //         }
    //     }
    //     return tempWinner;
    // };

    // vm.getColumns = function(){
    //     var columns = [];
    //     for (var j = 0; j < vm.boardState[0].length; j++) {
    //         var column = [];
    //         for (var k = 0; k < vm.boardState.length; k++) {
    //             column.push(vm.boardState[k][j]);
    //         }
    //         columns.push(column);
    //     }
    //     return columns;
    // };

    // vm.getDiags = function(arr) {
    //     if (typeof arr === 'undefined') arr = vm.boardState;
    //     var diags = [];
    //     for (var i = -5; i < 7; i++) {
    //         var group = [];
    //         for (var j = 0; j < 6; j++) {
    //             if ((i + j) >= 0 && (i + j) < 7) {
    //                 group.push(arr[j][i + j]);
    //             }
    //         }
    //         diags.push(group);
    //     }
    //     for (i = 0; i < 12; i++) {
    //         var group = [];
    //         for (var j = 5; j >= 0; j--) {
    //             if ((i - j) >= 0 && (i - j) < 7) {
    //                 group.push(arr[j][i - j]);
    //             }
    //         }
    //         diags.push(group);
    //     }
    //     return diags.filter(function(a) {
    //         return a.length > 3;
    //     });
    // };

    // vm.ai = function(){
        // var decision = null;
//         function threatDetect(lt, type) {
//             //vertical threat assessment & response
//             var columns = vm.getColumns();
//             for (var i = 0; i < columns.length; i++) {
//                 var vertMatch;
//                 type == 'major' ? vertMatch = "0"+lt+lt+lt : vertMatch = "00"+lt+lt;
//                 var colMatch = columns[i].join('').match(vertMatch);
//                 if (colMatch) {
//                     decision = i;
//                     console.log('ai: responding to a '+type+' vertical '+responseType);
//                     vm.aiComments.push('ai: responding to a '+type+' vertical '+responseType);
//                 }
//             }

//             if (!decision) {
//                 //horiz threat assessment & response
//                 var horizThreatPatterns;
//                 if (type == 'major') {
//                     horizThreatPatterns = ['0'+lt+lt+lt, lt+'0'+lt+lt, lt+lt+'0'+lt, lt+lt+lt+'0'];
//                 }
//                 else {
//                     horizThreatPatterns = ['00'+lt+lt, '0'+lt+lt+'0', '0'+lt+'0'+lt, lt+'0'+lt+'0', '0'+lt+lt+'0', lt+lt+'00'];
//                 }

//                 for (i = 0; i < vm.boardState.length; i++) {
//                     var found = [];
//                     var joined = vm.boardState[i].join('');
//                     for (var j = 0; j < horizThreatPatterns.length; j++) {
//                         var match = joined.match(horizThreatPatterns[j]);
//                         if (match) found.push(match[0]);
//                     }
//                     if (found.length) {
//                         var testCase = 0;
//                         if (i == vm.boardState.length - 1) {
//                             if (found[0] == '00yy' || found[0] == '00rr') testCase = 1;
//                             decision = joined.indexOf(found[0])+found[0].indexOf('0')+testCase;
//                             console.log('ai: responding to a '+type+' horizontal '+responseType);
//                             vm.aiComments.push('ai: responding to a '+type+' horizontal '+responseType);
//                         }
//                         else {
//                             matchPosition = joined.indexOf(found[0])+found[0].indexOf('0');
//                             if (found[0] == '00yy' || found[0] == '00rr') matchPosition++;
//                             if (vm.boardState[i+1][matchPosition]!==0) {
//                                 decision = matchPosition;
//                                 console.log('ai: responding to a '+type+' horizontal '+responseType);
//                                 vm.aiComments.push('ai: responding to a '+type+' horizontal '+responseType);
//                             }
//                         }
//                     }
//                 }
//             }

//             if (!decision) {
//                 //diag threat assessment & response
//                 var diags = vm.getDiags();
//                 var diagThreatPatterns = ['0'+lt+lt+lt, lt+'0'+lt+lt, lt+lt+'0'+lt, lt+lt+lt+'0'];
//                 for (i = 0; i < diags.length; i++) {
//                     var found = [];
//                     var joined = diags[i].join('');
//                     for (var j = 0; j < diagThreatPatterns.length; j++) {
//                         var match = joined.match(diagThreatPatterns[j]);
//                         if (match) found.push(match[0]);
//                     }
//                     if (found.length) {
//                         for (var l = 0; l < found.length; l++) {
//                             diagMap = vm.getDiags([[0,1,2,3,4,5,6],[7,8,9,10,11,12,13],[14,15,16,17,18,19,20],[21,22,23,24,25,26,27],[28,29,30,31,32,33,34],[35,36,37,38,39,40,41]]);
//                             var vulnSlot = diagMap[i][found[l].indexOf('0')];
//                             if ( typeof vm.boardState[Math.floor(vulnSlot/7)+1] === 'undefined' || vm.boardState[Math.floor(vulnSlot/7)+1][(vulnSlot%7)] !== 0) {
//                                 decision = vulnSlot%7;
//                                 console.log('ai: responding to a '+type+' diagonal '+responseType);
//                                 vm.aiComments.push('ai: responding to a '+type+' diagonal '+responseType);
//                             }
//                         }
//                     }
//                 }
//             }
//         }

        // function opportunityDetect(type) {
        //     //detecting our opportunities is just like detecting threats (mostly, 3 extra patterns)
        //     //we want to be defensive over offensive, so we only look for opportunities
        //     //if there are no immediate threats
        //     responseType = 'opportunity';
        //     threatDetect(vm.active,type);
        // }

        //look for winning opportunities
        // opportunityDetect('major');

        //if none, look for major threats
        // if (decision === null) {
        //     var responseType = 'threat';
        //     threatDetect((vm.active == 'r' ? 'y' : 'r'), 'major');
        // }

        //if none look for minor opportunities
//         if (decision === null) {
//             opportunityDetect('minor');
//         }

//         //if none look for minor threats
//         if (decision === null) {
//             var responseType = 'threat';
//             threatDetect((vm.active == 'r' ? 'y' : 'r'), 'minor');
//         }

        // if (decision !== null && vm.boardState[0][decision] === 0) {
        //     vm.drop(0,decision);
        // }
        // else {
        //     console.log('ai: no threats or opportunities found, goin random');
        //     var random = Math.floor(Math.random() * 7);
        //     var failSafe = 0;
        //     var boardValue = vm.boardState[0][random];
        //     while (boardValue !== 0 && failSafe < 100) {
        //         random = Math.floor(Math.random() * 7);
        //         boardValue = vm.boardState[0][random];
        //         failSafe++;
        //     }
        //     vm.drop(0,random);
        // }
    // };