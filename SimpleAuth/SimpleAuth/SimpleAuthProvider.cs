using MediaBrowser.Controller.Authentication;
using MediaBrowser.Controller.Entities;
using MediaBrowser.Controller.Library;
using MediaBrowser.Model.Logging;
using System;
using System.Threading.Tasks;


namespace SimpleAuth
{
    public class SimpleAuthProvider : IAuthenticationProvider
    {
        private readonly ILogger _logger;
        private readonly IUserManager _userManager;

        public SimpleAuthProvider(ILogger logger, IUserManager um) 
        {
            _logger = logger;
            _userManager = um;
        }

        public string Name
        {
            get { return "Simple Auth"; } 
        }

        public bool IsEnabled
        { 
            get { return true; }
        }

        public Task<ProviderAuthenticationResult> Authenticate(string username, string password)
        {
            _logger.Info("Authenticating User : " + username);
            User user = _userManager.GetUserByName(username);
            if (user != null)
            {
                _logger.Info("User Password    : (" + (user.Password ?? "null") + ")");
                _logger.Info("Entered Password : (" + (password ?? "null") + ")");
                if (string.IsNullOrEmpty(user.Password) && string.IsNullOrEmpty(password))
                {
                    _logger.Info("Login worked (empty)");
                    return Task.FromResult(new ProviderAuthenticationResult());
                }
                else if (user.Password == password)
                {
                    _logger.Info("Login worked (matched)");
                    return Task.FromResult(new ProviderAuthenticationResult());
                }
                else
                {
                    _logger.Info("Login failed - Incorrect Password");
                    throw new Exception("Login failed - Incorrect Password");
                }
            }
            else
            {
                _logger.Info("Login failed - User Not Found");
                throw new Exception("Login failed - User Not Found");
            }
        }

        public Task<bool> HasPassword(User user)
        {
            bool has_pw = true;
            if(string.IsNullOrEmpty(user.Password))
            {
                has_pw = false;
            }
            return Task.FromResult(has_pw);
        }

        public Task ChangePassword(User user, string newPassword)
        {
            user.Password = newPassword;
            _userManager.UpdateUser(user);
            return Task.CompletedTask;
        }

    }
}
