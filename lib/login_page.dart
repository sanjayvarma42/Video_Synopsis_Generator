import 'package:flutter/material.dart';
import 'package:hive/hive.dart';
import 'home_page.dart';
import 'register_page.dart';

class LoginPage extends StatelessWidget {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  final _formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Login"), backgroundColor: Colors.lightBlueAccent),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Form(
            key: _formKey,
            child: Column(children: [
              Text("Welcome Back", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              SizedBox(height: 20),
              TextFormField(
                controller: emailController,
                decoration: InputDecoration(
                  labelText: "Email",
                  prefixIcon: Icon(Icons.email),
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || !value.endsWith("@gmail.com")) {
                    return "Enter a valid Gmail address";
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: passwordController,
                obscureText: true,
                decoration: InputDecoration(
                  labelText: "Password",
                  prefixIcon: Icon(Icons.lock),
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.length < 6) {
                    return "Password must be at least 6 characters";
                  }
                  return null;
                },
              ),
              SizedBox(height: 20),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.lightBlueAccent,
                  padding: EdgeInsets.symmetric(horizontal: 50, vertical: 12),
                  textStyle: TextStyle(fontSize: 16),
                ),
                onPressed: () {
                  if (_formKey.currentState!.validate()) {
                    final usersBox = Hive.box('users');
                    final email = emailController.text;
                    final password = passwordController.text;
                    final user = usersBox.get(email);

                    if (user != null && user['password'] == password) {
                      Navigator.pushReplacement(context, MaterialPageRoute(
                        builder: (_) => HomePage(username: user['username']),
                      ));
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text("Invalid email or password")),
                      );
                    }
                  }
                },
                child: Text("Login"),
              ),
              SizedBox(height: 10),
              TextButton(
                child: Text("Don't have an account? Register"),
                onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => RegisterPage())),
              )
            ]),
          ),
        ),
      ),
    );
  }
}
